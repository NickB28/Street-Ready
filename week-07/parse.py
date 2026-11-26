# ruff: noqa: E501
"""Parse OpenSSH syslog lines into typed events, one line at a time (streaming)."""
import ipaddress
import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

# --- Regexes written by Nick (see week-07/my_regexes.txt) -------------------
LINE_RE = re.compile(
    r"^(?P<month>\w+)\s+(?P<day>\d+)\s+(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})"
    r"\s+(?P<host>\S+)\s+(?P<process>\w+)\[(?P<pid>\d+)\]:\s+(?P<message>.*)$"
)
FAILED_RE = re.compile(
    r"Failed password for (?:invalid user )?(?P<user>.+?) from (?P<ip>\S+) port (?P<port>\d+)"
)
ACCEPTED_RE = re.compile(
    r"Accepted password for (?P<user>\S+) from (?P<ip>\S+) port (?P<port>\d+)"
)
INVALID_RE = re.compile(r"Invalid user (?P<user>\S+) from (?P<ip>\S+)")
DISCONNECT_RE = re.compile(r"Received disconnect from (?P<ip>[^:]+):")
# --- Written by Claude, not Nick: "message repeated N times: [ ... ]" --------
REPEAT_RE = re.compile(r"message repeated (?P<count>\d+) times: \[ (?P<inner>.*)\]$")

MONTHS = {
    name: number
    for number, name in enumerate(
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        start=1,
    )
}


class Kind(Enum):
    FAILED_PASSWORD = "failed_password"
    INVALID_USER = "invalid_user"
    ACCEPTED = "accepted"
    DISCONNECT = "disconnect"
    BREAKIN_ATTEMPT = "breakin_attempt"
    OTHER = "other"


@dataclass(frozen=True)
class Event:
    timestamp: datetime
    host: str
    pid: int
    kind: Kind
    user: str | None
    ip: str | None
    port: int | None
    invalid_user: bool
    count: int = 1  # a "message repeated 5 times" line is one Event with count 5


@dataclass
class ParseStats:
    lines: int = 0
    unmatched: int = 0
    unmatched_first: list[int] = field(default_factory=list)  # first 5 line numbers
    bad_bytes_lines: int = 0
    invalid_ips: int = 0


def _valid_ip(text: str, stats: ParseStats) -> str | None:
    try:
        return str(ipaddress.ip_address(text))
    except ValueError:
        stats.invalid_ips += 1
        return None


def _classify(message: str, stats: ParseStats) -> tuple[Kind, str | None, str | None, int | None, bool]:
    found = FAILED_RE.match(message)
    if found:
        invalid = message.startswith("Failed password for invalid user ")
        return (Kind.FAILED_PASSWORD, found["user"], _valid_ip(found["ip"], stats),
                int(found["port"]), invalid)
    found = ACCEPTED_RE.match(message)
    if found:
        return (Kind.ACCEPTED, found["user"], _valid_ip(found["ip"], stats),
                int(found["port"]), False)
    found = INVALID_RE.match(message)
    if found:
        return Kind.INVALID_USER, found["user"], _valid_ip(found["ip"], stats), None, True
    found = DISCONNECT_RE.match(message)
    if found:
        return Kind.DISCONNECT, None, _valid_ip(found["ip"], stats), None, False
    if "POSSIBLE BREAK-IN ATTEMPT" in message:
        return Kind.BREAKIN_ATTEMPT, None, None, None, False
    return Kind.OTHER, None, None, None, False


def parse_lines(raw_lines: Iterable[bytes | str], year: int, stats: ParseStats) -> Iterator[Event]:
    previous_month = 0
    for number, raw in enumerate(raw_lines, start=1):
        stats.lines += 1
        if isinstance(raw, bytes):
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                stats.bad_bytes_lines += 1
                text = raw.decode("utf-8", errors="replace")
        else:
            text = raw
        text = text.rstrip("\r\n")

        line = LINE_RE.match(text)
        month = MONTHS.get(line["month"]) if line else None
        timestamp = None
        if line and month:
            if month < previous_month:  # Dec -> Jan: the year rolled over
                year += 1
            previous_month = month
            try:
                timestamp = datetime(year, month, int(line["day"]), int(line["hour"]),
                                     int(line["minute"]), int(line["second"]))
            except ValueError:  # e.g. Feb 30
                timestamp = None
        if line is None or timestamp is None:
            stats.unmatched += 1
            if len(stats.unmatched_first) < 5:
                stats.unmatched_first.append(number)
            continue

        message = line["message"]
        count = 1
        repeat = REPEAT_RE.match(message)
        if repeat:
            count = int(repeat["count"])
            message = repeat["inner"]
        kind, user, ip, port, invalid = _classify(message, stats)
        yield Event(timestamp, line["host"], int(line["pid"]), kind, user, ip, port,
                    invalid, count)


def parse_file(path: Path, year: int, stats: ParseStats) -> Iterator[Event]:
    with open(path, "rb") as handle:
        yield from parse_lines(handle, year, stats)