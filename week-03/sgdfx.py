"""sgdfx: look up and convert the MAS daily SGD per USD rates."""

import argparse
import bisect
import csv
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

DEFAULT_FILE = Path(__file__).parent / "data" / "sgd_usd_daily.csv"
TWO_PLACES = Decimal("0.01")


class DataError(Exception):
    """A problem with the data or the request that the user can fix."""


def parse_date(text):
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"not a valid date (use YYYY-MM-DD): {text}"
        ) from None


def parse_amount(text):
    try:
        amount = Decimal(text)
    except InvalidOperation:
        raise argparse.ArgumentTypeError(f"not a valid amount: {text}") from None
    if not amount.is_finite():
        raise argparse.ArgumentTypeError(f"not a valid amount: {text}")
    return amount


def load_rates(path):
    """Read the CSV and return (rates, skipped).

    rates is a list of (date, Decimal) sorted by date.
    skipped is how many blank or malformed rows were ignored.
    """
    rates = []
    skipped = 0
    try:
        with open(path, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                try:
                    day = datetime.strptime(row["date"], "%Y-%m-%d").date()
                    rate = Decimal(row["exchange_rate_usd"])
                except (KeyError, TypeError, ValueError, InvalidOperation):
                    skipped += 1
                    continue
                if not rate.is_finite() or rate <= 0:
                    skipped += 1
                    continue
                rates.append((day, rate))
    except (OSError, UnicodeDecodeError, csv.Error) as err:
        reason = getattr(err, "strerror", None) or err
        raise DataError(f"cannot read {path}: {reason}") from err
    if not rates:
        raise DataError(f"no valid rates found in {path}")
    rates.sort()
    return rates, skipped


def rate_on(rates, day):
    """Return (date, rate) for day, or the most recent earlier row."""
    dates = [d for d, _ in rates]
    index = bisect.bisect_right(dates, day)
    if index == 0:
        raise DataError(f"no data on or before {day} (data starts {rates[0][0]})")
    return rates[index - 1]


def stats_between(rates, start, end):
    """Return min, max, mean and the biggest move between consecutive rows."""
    if start > end:
        raise DataError(f"start date {start} is after end date {end}")
    window = [(d, r) for d, r in rates if start <= d <= end]
    if not window:
        raise DataError(f"no rates between {start} and {end}")
    values = [r for _, r in window]
    biggest = None
    for (_, before), (day, after) in zip(window, window[1:]):
        move = abs(after - before)
        if biggest is None or move > biggest[0]:
            biggest = (move, day)
    return {
        "min": min(values),
        "max": max(values),
        "mean": sum(values) / len(values),
        "move": biggest[0] if biggest else None,
        "move_date": biggest[1] if biggest else None,
    }


def convert(amount, currency, rate):
    """Convert amount using a SGD-per-USD rate. currency is what you have."""
    try:
        result = amount * rate if currency == "USD" else amount / rate
        return result.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    except ArithmeticError:
        raise DataError("amount is too large to convert") from None