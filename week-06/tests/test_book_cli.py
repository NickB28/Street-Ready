from pathlib import Path

import pytest
from book_cli import main

ORDERS_FILE = Path(__file__).parent.parent / "data" / "orders.csv"


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "orders.csv"
    path.write_text(text, encoding="utf-8")
    return path


def test_replay_prints_trades_best_prices_and_levels(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write(tmp_path, "ADD,1,SELL,3750,200\nADD,2,BUY,3750,100\n")
    assert main(["replay", str(path)]) == 0
    out = capsys.readouterr().out
    assert "Trades (1):" in out
    assert "buy #2 sell #1 S$37.50 x 100" in out
    assert "Best bid: none" in out
    assert "Best ask: S$37.50" in out
    assert "100 shares" in out


def test_the_hand_written_orders_file_gives_the_worked_out_result(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["replay", str(ORDERS_FILE)]) == 0
    out = capsys.readouterr().out
    assert "Trades (13):" in out
    assert "buy #14 sell #13 S$37.40 x 300" in out
    assert "buy #14 sell #3 S$37.50 x 200" in out
    assert "buy #14 sell #1 S$37.60 x 100" in out
    assert "Best bid: S$37.10" in out
    assert "Best ask: S$37.20" in out


def test_duplicate_id_exits_1_naming_file_and_line(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write(tmp_path, "ADD,1,BUY,3700,100\nADD,1,BUY,3700,100\n")
    assert main(["replay", str(path)]) == 1
    err = capsys.readouterr().err
    assert f"{path}:2:" in err
    assert "duplicate order id 1" in err


def test_cancel_of_an_unknown_id_exits_1_naming_file_and_line(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write(tmp_path, "ADD,1,BUY,3700,100\nCANCEL,9\n")
    assert main(["replay", str(path)]) == 1
    err = capsys.readouterr().err
    assert f"{path}:2:" in err
    assert "unknown order id 9" in err


def test_missing_file_exits_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["replay", str(tmp_path / "nope.csv")]) == 1
    assert "cannot read file" in capsys.readouterr().err


@pytest.mark.parametrize("price", ["37.5", "abc", "0", "-5", ""])
def test_bad_price_exits_1_naming_the_line(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], price: str
) -> None:
    path = write(tmp_path, f"ADD,1,BUY,3700,100\nADD,2,BUY,{price},100\n")
    assert main(["replay", str(path)]) == 1
    err = capsys.readouterr().err
    assert f"{path}:2:" in err
    assert "price" in err


@pytest.mark.parametrize("qty", ["150", "0", "abc", "-100", "50"])
def test_bad_quantity_exits_1_naming_the_line(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], qty: str
) -> None:
    path = write(tmp_path, f"ADD,1,BUY,3700,{qty}\n")
    assert main(["replay", str(path)]) == 1
    err = capsys.readouterr().err
    assert f"{path}:1:" in err
    assert "quantity" in err


@pytest.mark.parametrize("line", ["ADD,1,HOLD,3700,100", "FOO,1", "ADD,1,BUY,3700", "CANCEL"])
def test_malformed_lines_exit_1_without_a_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], line: str
) -> None:
    path = write(tmp_path, line + "\n")
    assert main(["replay", str(path)]) == 1
    err = capsys.readouterr().err
    assert f"{path}:1:" in err
    assert "Traceback" not in err


@pytest.mark.parametrize("argv", [[], ["bogus"], ["replay"]])
def test_usage_errors_exit_2(argv: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    assert main(argv) == 2
    assert "usage" in capsys.readouterr().err.lower()