# ruff: noqa: E501
"""sshwatch: attack report from an OpenSSH syslog file."""
import argparse
import json
import sys
from pathlib import Path
from typing import Any

from analyse import analyse
from parse import ParseStats, parse_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sshwatch")
    commands = parser.add_subparsers(dest="command", required=True)
    report = commands.add_parser("report", help="print an attack report")
    report.add_argument("path", type=Path)
    report.add_argument("--year", type=int, required=True, help="year of the first log line")
    report.add_argument("--top", type=int, default=10)
    report.add_argument("--window", type=int, default=5, help="window in minutes")
    report.add_argument("--threshold", type=int, default=10, help="failures in the window")
    report.add_argument("--format", choices=["text", "json"], default="text")
    return parser


def format_text(report: dict[str, Any]) -> str:
    stats = report["file_stats"]
    lines = [
        "SSH ATTACK REPORT",
        f"Lines read: {stats['lines']}   unmatched: {stats['unmatched']} "
        f"(first: {stats['unmatched_first_lines']})   lines with bad bytes: {stats['bad_bytes_lines']}"
        f"   invalid IPs: {stats['invalid_ips']}",
        "",
        "Events by kind:",
    ]
    lines += [f"  {kind:<16}{count:>8}" for kind, count in report["totals_by_kind"].items()]
    lines += ["", "Top source IPs by failed attempts:"]
    lines += [f"  {item['ip']:<40}{item['failures']:>8}" for item in report["top_ips"]]
    lines += ["", "Top usernames tried (existing users):"]
    lines += [f"  {item['name']:<20}{item['count']:>8}" for item in report["top_valid_users"]]
    lines += ["", "Top usernames tried (invalid users):"]
    lines += [f"  {item['name']:<20}{item['count']:>8}" for item in report["top_invalid_users"]]
    lines += ["", "Successful logins:"]
    for login in report["successful_logins"]:
        flag = "  <-- SUSPICIOUS" if login["suspicious"] else ""
        lines.append(f"  {login['time']}  {login['user']}  {login['ip']}  "
                     f"(failures before: {login['failures_before']}){flag}")
    settings = report["settings"]
    lines += ["", f"Brute force: >= {settings['threshold']} failures within "
              f"{settings['window_minutes']} min (edge inclusive):"]
    for item in report["brute_force_ips"]:
        lines.append(f"  {item['ip']:<40} first {item['first_seen']}  last {item['last_seen']}  "
                     f"peak {item['peak_in_window']}")
    lines += ["", "Failures per hour of day:"]
    lines += [f"  {hour:02d}:00  {count}" for hour, count in enumerate(report["failures_per_hour"])]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as error:
        return int(error.code) if isinstance(error.code, int) else 2
    if not 1970 <= args.year <= 9999:
        print(f"sshwatch: error: bad year {args.year}", file=sys.stderr)
        return 2
    if args.threshold < 1 or args.window < 1 or args.top < 1:
        print("sshwatch: error: --threshold, --window and --top must be at least 1", file=sys.stderr)
        return 2
    stats = ParseStats()
    try:
        report = analyse(parse_file(args.path, args.year, stats), stats,
                         args.top, args.window, args.threshold)
    except OSError as error:
        print(f"sshwatch: error: cannot read {args.path}: {error.strerror or error}", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_text(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())