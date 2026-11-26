# ruff: noqa: E501
import json
from pathlib import Path

import pytest
from sshwatch import main

LOG = (
    "Dec 10 10:00:00 LabSZ sshd[1]: Failed password for root from 1.2.3.4 port 22 ssh2\n"
    "Dec 10 10:00:01 LabSZ sshd[1]: Accepted password for root from 1.2.3.4 port 22 ssh2\n"
)


@pytest.fixture
def log_file(tmp_path: Path) -> Path:
    path = tmp_path / "ssh.log"
    path.write_text(LOG)
    return path


def test_text_report(log_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["report", str(log_file), "--year", "2026"]) == 0
    out = capsys.readouterr().out
    assert "SSH ATTACK REPORT" in out
    assert "1.2.3.4" in out


def test_json_report_is_valid_with_stable_keys(
    log_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["report", str(log_file), "--year", "2026", "--format", "json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert sorted(data) == [
        "brute_force_ips", "failures_per_hour", "file_stats", "settings",
        "successful_logins", "top_invalid_users", "top_ips", "top_valid_users", "totals_by_kind",
    ]


def test_missing_file_exits_1(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    assert main(["report", str(tmp_path / "nope.log"), "--year", "2026"]) == 1
    assert "sshwatch: error" in capsys.readouterr().err


def test_directory_exits_1(tmp_path: Path) -> None:
    assert main(["report", str(tmp_path), "--year", "2026"]) == 1


@pytest.mark.parametrize("year", ["20", "99999"])
def test_bad_year_exits_2(log_file: Path, year: str) -> None:
    assert main(["report", str(log_file), "--year", year]) == 2


def test_threshold_below_one_exits_2(log_file: Path) -> None:
    assert main(["report", str(log_file), "--year", "2026", "--threshold", "0"]) == 2


def test_missing_year_exits_2(log_file: Path) -> None:
    assert main(["report", str(log_file)]) == 2


def test_binary_file_does_not_crash(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "bin.log"
    path.write_bytes(bytes(range(256)) * 20)
    assert main(["report", str(path), "--year", "2026"]) == 0
    assert "Traceback" not in capsys.readouterr().err


def test_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "empty.log"
    path.write_bytes(b"")
    assert main(["report", str(path), "--year", "2026"]) == 0


def test_file_with_bad_bytes_is_reported(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "bad.log"
    path.write_bytes(LOG.encode() + b"Dec 10 10:00:02 LabSZ sshd[1]: Invalid user \xff from 1.2.3.4\n")
    assert main(["report", str(path), "--year", "2026", "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["file_stats"]["bad_bytes_lines"] == 1