from pathlib import Path

import hdb_cli
import pytest
from hdb import load_sales

SAMPLE = Path(__file__).parent.parent / "data" / "sample.csv"
HEADER = (
    "month,town,flat_type,block,street_name,storey_range,floor_area_sqm,"
    "flat_model,lease_commence_date,remaining_lease,resale_price"
)


def row(town: str, flat_type: str, price: int, month: str = "2019-01") -> str:
    """Build one full CSV row, changing only the fields a test cares about."""
    return f"{month},{town},{flat_type},1,MAIN ST,01 TO 03,90,Model A,1990,60 years,{price}"


def write_file(tmp_path: Path, *rows: str) -> Path:
    """Write a resale CSV with the real header plus the given rows."""
    path = tmp_path / "resale.csv"
    path.write_text(HEADER + "\n" + "\n".join(rows) + "\n")
    return path


def run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str, str]:
    """Call main with argv and return the exit code, stdout and stderr."""
    code = hdb_cli.main(list(argv))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_range_on_the_sample_matches_a_brute_force_count(
    capsys: pytest.CaptureFixture[str],
) -> None:
    sales, _ = load_sales(SAMPLE)
    flat_type = sales[0].flat_type
    low, high = 400_000, 700_000
    expected = sum(
        1 for s in sales if s.flat_type == flat_type and low <= s.resale_price <= high
    )
    code, out, err = run(
        capsys, "range", str(SAMPLE), "--flat-type", flat_type.lower(),
        "--min", str(low), "--max", str(high),
    )
    assert code == 0
    assert f"Sales in band: {expected}" in out


def test_range_reports_median_and_the_cheapest_and_dearest(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    path = write_file(
        tmp_path,
        row("BEDOK", "4 ROOM", 100_000),
        row("BISHAN", "4 ROOM", 200_000),
        row("TAMPINES", "4 ROOM", 300_000),
        row("YISHUN", "4 ROOM", 400_000),
        row("BEDOK", "4 ROOM", 900_000),
        row("BEDOK", "3 ROOM", 250_000),
    )
    code, out, _ = run(
        capsys, "range", str(path), "--flat-type", "4 ROOM", "--min", "150000", "--max", "400000"
    )
    assert code == 0
    assert "Sales in band: 3" in out
    assert "Median price: S$300,000" in out
    assert "Cheapest: BISHAN S$200,000" in out
    assert "Dearest: YISHUN S$400,000" in out
    code, out, _ = run(
        capsys, "range", str(path), "--flat-type", "4 ROOM", "--min", "100000", "--max", "400000"
    )
    assert "Sales in band: 4" in out
    assert "Median price: S$250,000" in out


def test_range_with_no_sales_in_the_band_says_so(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    path = write_file(tmp_path, row("BEDOK", "4 ROOM", 500_000))
    code, out, _ = run(
        capsys, "range", str(path), "--flat-type", "4 ROOM", "--min", "1000", "--max", "2000"
    )
    assert code == 0
    assert "Sales in band: 0" in out
    assert "No sales in this band." in out


def test_top_lists_the_dearest_sales_first(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    path = write_file(
        tmp_path,
        row("TAMPINES", "4 ROOM", 300_000),
        row("TAMPINES", "4 ROOM", 500_000),
        row("TAMPINES", "5 ROOM", 400_000),
        row("BEDOK", "4 ROOM", 900_000),
    )
    code, out, _ = run(capsys, "top", str(path), "--town", "tampines", "-n", "2")
    assert code == 0
    assert out.index("S$500,000") < out.index("S$400,000")
    assert "S$900,000" not in out
    assert "S$300,000" not in out


def test_unknown_flat_type_and_unknown_town_exit_1(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    path = write_file(tmp_path, row("BEDOK", "4 ROOM", 500_000))
    code, out, err = run(capsys, "range", str(path), "--flat-type", "9 ROOM")
    assert code == 1
    assert "unknown flat type" in err
    assert "Traceback" not in err
    code, out, err = run(capsys, "top", str(path), "--town", "NOWHERE")
    assert code == 1
    assert "unknown town" in err


def test_missing_file_exits_1_without_a_traceback(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    code, out, err = run(
        capsys, "range", str(tmp_path / "nope.csv"), "--flat-type", "4 ROOM"
    )
    assert code == 1
    assert "cannot read" in err
    assert "Traceback" not in err


def test_usage_errors_exit_2(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, err = run(capsys)
    assert code == 2
    code, out, err = run(capsys, "top", str(SAMPLE), "--town", "BEDOK", "-n", "0")
    assert code == 2
    assert "at least 1" in err


def test_bad_rows_are_reported_but_the_query_still_runs(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    path = write_file(
        tmp_path, row("BEDOK", "4 ROOM", 500_000), "2019-01,BAD", row("BEDOK", "4 ROOM", 0)
    )
    code, out, err = run(capsys, "top", str(path), "--town", "BEDOK")
    assert code == 0
    assert "skipped 2" in err
    assert "S$500,000" in out


def test_min_above_max_exits_1(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    path = write_file(tmp_path, row("BEDOK", "4 ROOM", 500_000))
    code, out, err = run(
        capsys, "range", str(path), "--flat-type", "4 ROOM", "--min", "9", "--max", "1"
    )
    assert code == 1
    assert "above" in err