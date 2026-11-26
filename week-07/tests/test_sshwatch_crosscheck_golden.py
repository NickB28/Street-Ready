import json
from pathlib import Path

import pytest
from analyse import analyse
from parse import ParseStats, parse_file
from sshwatch import main

DATA = Path(__file__).parent.parent / "data" / "OpenSSH_2k.log"
GOLDEN = Path(__file__).parent / "golden_2k.json"

# Independent count, run in PowerShell (it does not use any of my code):
#   (Select-String -Path week-07\data\OpenSSH_2k.log -Pattern "Failed password" -SimpleMatch).Count
SELECT_STRING_FAILED_PASSWORD_LINES = 520


def repeat_extra() -> int:
    """A "message repeated N times: [ Failed password ...]" line is one line but N failures."""
    extra = 0
    for line in DATA.read_text(encoding="utf-8", errors="replace").splitlines():
        if "message repeated" in line and "Failed password" in line:
            extra += int(line.split("message repeated ")[1].split(" times")[0]) - 1
    return extra


def test_failed_password_total_matches_the_select_string_count() -> None:
    stats = ParseStats()
    report = analyse(parse_file(DATA, 2026, stats), stats)
    expected = SELECT_STRING_FAILED_PASSWORD_LINES + repeat_extra()
    assert report["totals_by_kind"]["FAILED_PASSWORD"] == expected


def test_every_line_of_the_2k_file_is_parsed() -> None:
    stats = ParseStats()
    analyse(parse_file(DATA, 2026, stats), stats)
    assert stats.lines == 2000
    assert stats.unmatched == 0


def test_json_report_equals_the_golden_file(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["report", str(DATA), "--year", "2026", "--format", "json"]) == 0
    actual = json.loads(capsys.readouterr().out)
    expected = json.loads(GOLDEN.read_text(encoding="utf-8-sig"))
    assert actual == expected