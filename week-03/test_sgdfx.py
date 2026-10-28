from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

import sgdfx

FIXTURE = Path(__file__).parent / "fixtures" / "rates_fixture.csv"


def run(capsys, *argv):
    code = sgdfx.main(list(argv))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_latest_shows_most_recent_rate(capsys):
    code, out, _ = run(capsys, "--file", str(FIXTURE), "latest")
    assert code == 0
    assert "2015-03-19" in out
    assert "1.4050" in out


def test_on_exact_date(capsys):
    code, out, _ = run(capsys, "--file", str(FIXTURE), "on", "2015-03-04")
    assert code == 0
    assert "1.3690" in out
    assert "No rate" not in out


def test_weekend_falls_back_and_says_so(capsys):
    code, out, _ = run(capsys, "--file", str(FIXTURE), "on", "2015-03-07")
    assert code == 0
    assert "No rate for 2015-03-07" in out
    assert "using 2015-03-06" in out
    assert "1.3800" in out


def test_blank_rate_day_falls_back(capsys):
    code, out, _ = run(capsys, "--file", str(FIXTURE), "on", "2015-03-10")
    assert code == 0
    assert "using 2015-03-09" in out


def test_date_before_data_is_a_data_error(capsys):
    code, out, err = run(capsys, "--file", str(FIXTURE), "on", "2010-01-01")
    assert code == 1
    assert "no data on or before 2010-01-01" in err
    assert "Traceback" not in err


def test_convert_usd_to_sgd(capsys):
    code, out, _ = run(
        capsys, "--file", str(FIXTURE), "convert", "100", "--from", "USD",
        "--date", "2015-03-02",
    )
    assert code == 0
    assert "100 USD = 137.00 SGD" in out


def test_convert_sgd_to_usd(capsys):
    code, out, _ = run(
        capsys, "--file", str(FIXTURE), "convert", "137", "--from", "SGD",
        "--date", "2015-03-02",
    )
    assert code == 0
    assert "137 SGD = 100.00 USD" in out


def test_convert_defaults_to_latest_rate(capsys):
    code, out, _ = run(capsys, "--file", str(FIXTURE), "convert", "10", "--from", "USD")
    assert code == 0
    assert "10 USD = 14.05 SGD" in out
    assert "2015-03-19" in out


def test_negative_amount_is_a_data_error(capsys):
    code, out, err = run(capsys, "--file", str(FIXTURE), "convert", "-5", "--from", "USD")
    assert code == 1
    assert "must not be negative" in err


def test_stats_values(capsys):
    code, out, _ = run(
        capsys, "--file", str(FIXTURE), "stats", "--start", "2015-03-02",
        "--end", "2015-03-06",
    )
    assert code == 0
    assert "min   1.3690" in out
    assert "max   1.3800" in out
    assert "mean  1.3732" in out
    assert "biggest move  0.0060 on 2015-03-05" in out


def test_stats_empty_range_is_a_data_error(capsys):
    code, out, err = run(
        capsys, "--file", str(FIXTURE), "stats", "--start", "2020-01-01",
        "--end", "2020-01-31",
    )
    assert code == 1
    assert "no rates between" in err


def test_malformed_rows_are_skipped_and_counted(capsys):
    code, out, err = run(capsys, "--file", str(FIXTURE), "latest")
    assert code == 0
    assert "skipped 2 malformed rows" in err


def test_missing_file_is_a_data_error(capsys, tmp_path):
    code, out, err = run(capsys, "--file", str(tmp_path / "nope.csv"), "latest")
    assert code == 1
    assert "cannot read" in err
    assert "Traceback" not in err


def test_bad_date_is_a_usage_error(capsys):
    code, out, err = run(capsys, "--file", str(FIXTURE), "on", "banana")
    assert code == 2
    assert "not a valid date" in err


def test_no_subcommand_is_a_usage_error(capsys):
    code, out, err = run(capsys)
    assert code == 2


def test_file_with_no_valid_rows_is_a_data_error(capsys, tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("date,exchange_rate_usd\n2015-01-01,abc\n")
    code, out, err = run(capsys, "--file", str(bad), "latest")
    assert code == 1
    assert "no valid rates" in err


@pytest.mark.parametrize("amount", ["1e999", "nan"])
def test_unusable_amounts_never_traceback(capsys, amount):
    code, out, err = run(
        capsys, "--file", str(FIXTURE), "convert", amount, "--from", "USD"
    )
    assert code in (1, 2)
    assert "Traceback" not in err


def test_convert_uses_decimal_not_float():
    result = sgdfx.convert(Decimal("0.10"), "USD", Decimal("3"))
    assert result == Decimal("0.30")
    assert isinstance(result, Decimal)


def test_rate_on_returns_earlier_row():
    rates = [(date(2015, 3, 6), Decimal("1.38")), (date(2015, 3, 9), Decimal("1.39"))]
    assert sgdfx.rate_on(rates, date(2015, 3, 8)) == rates[0]