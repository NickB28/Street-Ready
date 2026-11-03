from pathlib import Path

import lotbook_cli
import pytest

EXAMPLES = Path(__file__).parent.parent / "examples"
TRADES = str(EXAMPLES / "trades.csv")
PRICES = str(EXAMPLES / "prices.csv")
BROKEN = str(EXAMPLES / "broken_trades.csv")
HEADER = "date,ticker,side,quantity,price\n"


def run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str, str]:
    """Call main with argv and return the exit code, stdout and stderr."""
    code = lotbook_cli.main(list(argv))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_report_happy_path(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, err = run(capsys, "report", TRADES, "--prices", PRICES)
    assert code == 0
    assert err == ""
    assert "189.47" in out
    assert "199.47" in out
    assert "Realised P&L: 540.10" in out


def test_broken_row_exits_1_and_names_the_row(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, err = run(capsys, "report", BROKEN, "--prices", PRICES)
    assert code == 1
    assert "broken_trades.csv row 3" in err
    assert "multiple of 100" in err
    assert out == ""
    assert "Traceback" not in err


def test_missing_trades_file_exits_1(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    code, out, err = run(
        capsys, "report", str(tmp_path / "nope.csv"), "--prices", PRICES
    )
    assert code == 1
    assert "cannot read" in err
    assert "Traceback" not in err


def test_missing_prices_file_exits_1(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    code, out, err = run(
        capsys, "report", TRADES, "--prices", str(tmp_path / "nope.csv")
    )
    assert code == 1
    assert "cannot read" in err


def test_no_arguments_is_a_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, err = run(capsys, "report")
    assert code == 2
    assert "required" in err


def test_held_ticker_without_a_price_exits_1(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    prices = tmp_path / "prices.csv"
    prices.write_text("ticker,price\nD05,37.50\n")
    code, out, err = run(capsys, "report", TRADES, "--prices", str(prices))
    assert code == 1
    assert "no price for O39" in err


def test_unreadable_value_names_the_row(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    trades = tmp_path / "trades.csv"
    trades.write_text(HEADER + "2026-10-01,D05,BUY,100,abc\n")
    code, out, err = run(capsys, "report", str(trades), "--prices", PRICES)
    assert code == 1
    assert "trades.csv row 2" in err
    assert "Traceback" not in err


def test_file_saved_with_a_utf8_bom_is_accepted(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    trades = tmp_path / "trades.csv"
    trades.write_text(HEADER + "2026-10-01,D05,BUY,100,35.20\n", encoding="utf-8-sig")
    code, out, err = run(capsys, "report", str(trades), "--prices", PRICES)
    assert code == 0
    assert "D05" in out