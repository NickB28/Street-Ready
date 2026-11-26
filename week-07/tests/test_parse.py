# ruff: noqa: E501
from datetime import datetime

import pytest
from parse import Kind, ParseStats, parse_lines

FAILED = "Dec 10 11:04:41 LabSZ sshd[25537]: Failed password for root from 183.62.140.253 port 36027 ssh2"
FAILED_INVALID = (
    "Dec 10 11:04:45 LabSZ sshd[25539]: Failed password for invalid user user "
    "from 103.99.0.122 port 52683 ssh2"
)
ACCEPTED = "Dec 10 09:32:20 LabSZ sshd[24680]: Accepted password for fztu from 119.137.62.142 port 49116 ssh2"
INVALID = "Dec 10 06:55:46 LabSZ sshd[24200]: Invalid user webmaster from 173.234.31.186"
DISCONNECT = "Dec 10 07:07:45 LabSZ sshd[24206]: Received disconnect from 52.80.34.196: 11: Bye Bye [preauth]"
BREAKIN = (
    "Dec 10 06:55:46 LabSZ sshd[24200]: reverse mapping checking getaddrinfo for "
    "ns.marryaldkfaczcz.com [173.234.31.186] failed - POSSIBLE BREAK-IN ATTEMPT!"
)
PAM = (
    "Dec 10 11:04:41 LabSZ sshd[25541]: pam_unix(sshd:auth): authentication failure; "
    "logname= uid=0 euid=0 tty=ssh ruser= rhost=183.62.140.253  user=root"
)


def parse(lines: list[str] | list[bytes], year: int = 2026) -> tuple[list, ParseStats]:  # type: ignore[type-arg]
    stats = ParseStats()
    return list(parse_lines(lines, year, stats)), stats


@pytest.mark.parametrize(
    ("line", "kind"),
    [
        (FAILED, Kind.FAILED_PASSWORD),
        (FAILED_INVALID, Kind.FAILED_PASSWORD),
        (ACCEPTED, Kind.ACCEPTED),
        (INVALID, Kind.INVALID_USER),
        (DISCONNECT, Kind.DISCONNECT),
        (BREAKIN, Kind.BREAKIN_ATTEMPT),
        (PAM, Kind.OTHER),
    ],
)
def test_each_message_kind_is_recognised(line: str, kind: Kind) -> None:
    events, stats = parse([line])
    assert [event.kind for event in events] == [kind]
    assert stats.unmatched == 0


def test_failed_password_fields() -> None:
    event = parse([FAILED])[0][0]
    assert (event.user, event.ip, event.port, event.pid, event.host) == (
        "root", "183.62.140.253", 36027, 25537, "LabSZ")
    assert event.invalid_user is False
    assert event.timestamp == datetime(2026, 12, 10, 11, 4, 41)


def test_failed_password_for_invalid_user_sets_the_flag() -> None:
    event = parse([FAILED_INVALID])[0][0]
    assert event.user == "user"
    assert event.invalid_user is True


def test_accepted_fields() -> None:
    event = parse([ACCEPTED])[0][0]
    assert (event.user, event.ip, event.port) == ("fztu", "119.137.62.142", 49116)


def test_invalid_user_fields() -> None:
    event = parse([INVALID])[0][0]
    assert (event.user, event.ip, event.invalid_user) == ("webmaster", "173.234.31.186", True)


def test_disconnect_has_the_ip() -> None:
    assert parse([DISCONNECT])[0][0].ip == "52.80.34.196"


def test_event_is_frozen() -> None:
    event = parse([FAILED])[0][0]
    with pytest.raises(AttributeError):
        event.user = "x"


def test_message_repeated_counts_as_five_failures() -> None:
    line = (
        "Dec 10 12:00:00 LabSZ sshd[1]: message repeated 5 times: "
        "[ Failed password for root from 5.36.59.76 port 22 ssh2]"
    )
    events, _ = parse([line])
    assert len(events) == 1
    assert events[0].count == 5
    assert events[0].kind is Kind.FAILED_PASSWORD
    assert events[0].ip == "5.36.59.76"


def test_single_digit_day_with_extra_space() -> None:
    line = "Jan  5 01:02:03 LabSZ sshd[1]: Invalid user bob from 1.2.3.4"
    assert parse([line])[0][0].timestamp == datetime(2026, 1, 5, 1, 2, 3)


def test_year_rolls_over_from_december_to_january() -> None:
    events, _ = parse([
        "Dec 31 23:59:59 LabSZ sshd[1]: Invalid user a from 1.2.3.4",
        "Jan  1 00:00:05 LabSZ sshd[1]: Invalid user a from 1.2.3.4",
    ])
    assert events[0].timestamp == datetime(2026, 12, 31, 23, 59, 59)
    assert events[1].timestamp == datetime(2027, 1, 1, 0, 0, 5)


def test_year_does_not_roll_over_within_a_year() -> None:
    events, _ = parse([INVALID, FAILED])
    assert {event.timestamp.year for event in events} == {2026}


def test_ipv6_source_address() -> None:
    line = "Dec 10 11:00:00 LabSZ sshd[1]: Failed password for root from 2001:db8::1 port 22 ssh2"
    assert parse([line])[0][0].ip == "2001:db8::1"


def test_invalid_ip_is_dropped_and_counted() -> None:
    line = "Dec 10 11:00:00 LabSZ sshd[1]: Failed password for root from 999.1.1.1 port 22 ssh2"
    events, stats = parse([line])
    assert events[0].ip is None
    assert stats.invalid_ips == 1


def test_bad_bytes_do_not_crash_and_are_counted() -> None:
    good = FAILED.encode()
    bad = b"Dec 10 11:04:41 LabSZ sshd[1]: Invalid user \xff\xfe from 1.2.3.4"
    events, stats = parse([good, bad])
    assert stats.bad_bytes_lines == 1
    assert len(events) >= 1


def test_unmatched_line_is_counted_with_its_line_number() -> None:
    events, stats = parse([FAILED, "this is not a log line", INVALID])
    assert len(events) == 2
    assert stats.unmatched == 1
    assert stats.unmatched_first == [2]


def test_only_the_first_five_unmatched_line_numbers_are_kept() -> None:
    _, stats = parse(["junk"] * 8)
    assert stats.unmatched == 8
    assert stats.unmatched_first == [1, 2, 3, 4, 5]


def test_empty_input() -> None:
    events, stats = parse([])
    assert events == []
    assert stats.lines == 0


def test_impossible_date_is_unmatched() -> None:
    _, stats = parse(["Feb 30 10:00:00 LabSZ sshd[1]: Invalid user a from 1.2.3.4"])
    assert stats.unmatched == 1


def test_unknown_month_is_unmatched() -> None:
    _, stats = parse(["Xyz 10 10:00:00 LabSZ sshd[1]: Invalid user a from 1.2.3.4"])
    assert stats.unmatched == 1


def test_crlf_line_endings_are_handled() -> None:
    events, stats = parse([FAILED.encode() + b"\r\n"])
    assert len(events) == 1
    assert stats.unmatched == 0