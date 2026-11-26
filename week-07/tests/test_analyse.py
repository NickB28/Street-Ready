# ruff: noqa: E501
from analyse import analyse
from parse import ParseStats, parse_lines


def run(lines: list[str], **kwargs: int) -> dict:  # type: ignore[type-arg]
    stats = ParseStats()
    return analyse(parse_lines(lines, 2026, stats), stats, **kwargs)


def failed(minute: int, second: int = 0, ip: str = "1.2.3.4", user: str = "root") -> str:
    return (f"Dec 10 10:{minute:02d}:{second:02d} LabSZ sshd[1]: "
            f"Failed password for {user} from {ip} port 22 ssh2")


def test_totals_per_kind() -> None:
    report = run([failed(0), failed(1),
                  "Dec 10 10:02:00 LabSZ sshd[1]: Invalid user a from 1.2.3.4"])
    assert report["totals_by_kind"]["FAILED_PASSWORD"] == 2
    assert report["totals_by_kind"]["INVALID_USER"] == 1


def test_repeated_lines_count_in_totals() -> None:
    report = run(["Dec 10 10:00:00 LabSZ sshd[1]: message repeated 5 times: "
                  "[ Failed password for root from 1.2.3.4 port 22 ssh2]"])
    assert report["totals_by_kind"]["FAILED_PASSWORD"] == 5
    assert report["top_ips"] == [{"ip": "1.2.3.4", "failures": 5}]


def test_top_ips_are_sorted_and_limited() -> None:
    lines = [failed(0, ip="1.1.1.1")] * 3 + [failed(1, ip="2.2.2.2")] * 5 + [failed(2, ip="3.3.3.3")]
    report = run(lines, top=2)
    assert [item["ip"] for item in report["top_ips"]] == ["2.2.2.2", "1.1.1.1"]


def test_usernames_split_into_valid_and_invalid() -> None:
    lines = [
        failed(0, user="root"),
        "Dec 10 10:01:00 LabSZ sshd[1]: Failed password for invalid user guest "
        "from 1.2.3.4 port 22 ssh2",
    ]
    report = run(lines)
    assert report["top_valid_users"] == [{"name": "root", "count": 1}]
    assert report["top_invalid_users"] == [{"name": "guest", "count": 1}]


def test_login_after_five_failures_is_flagged() -> None:
    lines = [failed(i) for i in range(5)]
    lines.append("Dec 10 10:10:00 LabSZ sshd[1]: Accepted password for root from 1.2.3.4 port 22 ssh2")
    login = run(lines)["successful_logins"][0]
    assert login["failures_before"] == 5
    assert login["suspicious"] is True


def test_login_after_four_failures_is_not_flagged() -> None:
    lines = [failed(i) for i in range(4)]
    lines.append("Dec 10 10:10:00 LabSZ sshd[1]: Accepted password for root from 1.2.3.4 port 22 ssh2")
    assert run(lines)["successful_logins"][0]["suspicious"] is False


def test_failures_per_hour() -> None:
    report = run([failed(0), failed(1)])
    assert report["failures_per_hour"][10] == 2
    assert sum(report["failures_per_hour"]) == 2


def test_window_edge_exactly_w_minutes_apart_is_inside() -> None:
    # 3 failures: 10:00:00, 10:02:30, 10:05:00. First and last are exactly 5 minutes apart.
    report = run([failed(0), failed(2, 30), failed(5)], window_minutes=5, threshold=3)
    assert report["brute_force_ips"][0]["peak_in_window"] == 3


def test_window_edge_one_second_too_late_is_outside() -> None:
    report = run([failed(0), failed(2, 30), failed(5, 1)], window_minutes=5, threshold=3)
    assert report["brute_force_ips"] == []


def test_threshold_is_inclusive() -> None:
    lines = [failed(0, i) for i in range(10)]
    assert len(run(lines, threshold=10)["brute_force_ips"]) == 1
    assert run(lines, threshold=11)["brute_force_ips"] == []


def test_brute_force_reports_first_last_and_peak() -> None:
    lines = [failed(0, i) for i in range(10)]
    item = run(lines)["brute_force_ips"][0]
    assert item["first_seen"] == "2026-12-10T10:00:00"
    assert item["last_seen"] == "2026-12-10T10:00:09"
    assert item["peak_in_window"] == 10


def test_slow_attacker_below_threshold_is_not_reported() -> None:
    lines = [failed(i * 10 % 60, ip="9.9.9.9") for i in range(6)]
    assert run(lines)["brute_force_ips"] == []


def test_each_ip_has_its_own_window() -> None:
    lines = []
    for i in range(6):
        lines += [failed(0, i, ip="1.1.1.1"), failed(0, i, ip="2.2.2.2")]
    report = run(lines, threshold=10)
    assert report["brute_force_ips"] == []


def test_window_is_linear_for_a_large_input() -> None:
    lines = [failed(i // 60 % 60, i % 60) for i in range(5000)]
    report = run(lines, threshold=1)
    assert report["top_ips"][0]["failures"] == 5000


def test_empty_input_gives_an_empty_report() -> None:
    report = run([])
    assert report["top_ips"] == []
    assert report["failures_per_hour"] == [0] * 24