# ruff: noqa: E501
"""Analyse parsed SSH events: totals, top IPs, usernames, logins, brute force, hours."""
from collections import Counter, deque
from collections.abc import Iterable
from datetime import timedelta
from typing import Any

from parse import Event, Kind, ParseStats

SUSPICIOUS_FAILURES = 5  # a login after this many earlier failures from the same IP is flagged


def analyse(
    events: Iterable[Event],
    stats: ParseStats,
    top: int = 10,
    window_minutes: int = 5,
    threshold: int = 10,
) -> dict[str, Any]:
    """Single pass over the events (they are in time order). Memory grows with the number of
    distinct IPs and usernames, not with the number of lines.

    Window rule (inclusive): failures exactly `window_minutes` apart are inside the same window.
    """
    window = timedelta(minutes=window_minutes)
    kinds: Counter[str] = Counter()
    failed_by_ip: Counter[str] = Counter()
    valid_users: Counter[str] = Counter()
    invalid_users: Counter[str] = Counter()
    hours = [0] * 24
    logins: list[dict[str, Any]] = []
    recent: dict[str, deque[tuple[Any, int]]] = {}  # ip -> (time, count) inside the window
    in_window: Counter[str] = Counter()  # ip -> failures currently inside the window
    peak: Counter[str] = Counter()
    first_seen: dict[str, Any] = {}
    last_seen: dict[str, Any] = {}

    for event in events:
        kinds[event.kind.name] += event.count
        if event.kind is Kind.FAILED_PASSWORD:
            hours[event.timestamp.hour] += event.count
            if event.user is not None:
                (invalid_users if event.invalid_user else valid_users)[event.user] += event.count
            if event.ip is None:
                continue
            failed_by_ip[event.ip] += event.count
            first_seen.setdefault(event.ip, event.timestamp)
            last_seen[event.ip] = event.timestamp
            queue = recent.setdefault(event.ip, deque())
            queue.append((event.timestamp, event.count))
            in_window[event.ip] += event.count
            # Drop entries older than the window. Each entry is added once and removed once,
            # so the whole pass is O(n), not "recount the window for every line".
            while queue and event.timestamp - queue[0][0] > window:
                in_window[event.ip] -= queue.popleft()[1]
            peak[event.ip] = max(peak[event.ip], in_window[event.ip])
        elif event.kind is Kind.ACCEPTED:
            before = failed_by_ip[event.ip] if event.ip else 0
            logins.append({
                "time": event.timestamp.isoformat(),
                "user": event.user,
                "ip": event.ip,
                "failures_before": before,
                "suspicious": before >= SUSPICIOUS_FAILURES,
            })

    brute_force = [
        {
            "ip": ip,
            "first_seen": first_seen[ip].isoformat(),
            "last_seen": last_seen[ip].isoformat(),
            "peak_in_window": peak[ip],
        }
        for ip in sorted(peak, key=lambda item: (-peak[item], item))
        if peak[ip] >= threshold
    ]

    def ranked(counter: Counter[str]) -> list[dict[str, Any]]:
        ordered = sorted(counter.items(), key=lambda pair: (-pair[1], pair[0]))
        return [{"name": name, "count": count} for name, count in ordered[:top]]

    return {
        "file_stats": {
            "lines": stats.lines,
            "unmatched": stats.unmatched,
            "unmatched_first_lines": list(stats.unmatched_first),
            "bad_bytes_lines": stats.bad_bytes_lines,
            "invalid_ips": stats.invalid_ips,
        },
        "settings": {"top": top, "window_minutes": window_minutes, "threshold": threshold},
        "totals_by_kind": {kind.name: kinds[kind.name] for kind in Kind},
        "top_ips": [{"ip": item["name"], "failures": item["count"]} for item in ranked(failed_by_ip)],
        "top_valid_users": ranked(valid_users),
        "top_invalid_users": ranked(invalid_users),
        "successful_logins": logins,
        "brute_force_ips": brute_force,
        "failures_per_hour": hours,
    }