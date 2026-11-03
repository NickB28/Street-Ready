"""lotbook command line: report positions and profit from two CSV files."""

import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from lotbook.errors import LotbookError
from lotbook.portfolio import Portfolio
from lotbook.trade import Side, Trade


class DataError(Exception):
    """A problem with an input file that the user can fix."""


def read_rows(path: Path) -> list[tuple[int, dict[str, str]]]:
    """Read a CSV file and return (row number, row) pairs. Row 1 is the header."""
    try:
        with open(path, newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            return [(reader.line_num, row) for row in reader]
    except (OSError, UnicodeDecodeError, csv.Error) as err:
        reason = getattr(err, "strerror", None) or err
        raise DataError(f"cannot read {path}: {reason}") from err


def parse_trade(row: dict[str, str], where: str) -> Trade:
    """Turn one CSV row into a Trade. where names the file and row for errors."""
    try:
        return Trade(
            date.fromisoformat(row["date"].strip()),
            row["ticker"].strip(),
            Side(row["side"].strip().upper()),
            int(row["quantity"]),
            Decimal(row["price"]),
        )
    except KeyError as err:
        raise DataError(f"{where}: missing column {err}") from None
    except LotbookError as err:
        raise DataError(f"{where}: {err}") from None
    except (AttributeError, TypeError, ValueError, InvalidOperation):
        raise DataError(
            f"{where}: cannot read this row (check date, side, quantity and price)"
        ) from None


def load_portfolio(path: Path) -> Portfolio:
    """Apply every trade in a CSV file, reporting the row of any broken rule."""
    portfolio = Portfolio()
    for number, row in read_rows(path):
        where = f"{path.name} row {number}"
        trade = parse_trade(row, where)
        try:
            portfolio.apply(trade)
        except LotbookError as err:
            raise DataError(f"{where}: {err}") from None
        except ArithmeticError:
            raise DataError(f"{where}: number too large") from None
    return portfolio


def read_prices(path: Path) -> dict[str, Decimal]:
    """Read a prices CSV (ticker, price) into a dict of ticker to price."""
    prices: dict[str, Decimal] = {}
    for number, row in read_rows(path):
        where = f"{path.name} row {number}"
        try:
            ticker = row["ticker"].strip()
            price = Decimal(row["price"])
        except (KeyError, AttributeError, TypeError, InvalidOperation):
            raise DataError(f"{where}: cannot read this row") from None
        if not price.is_finite() or price <= 0:
            raise DataError(f"{where}: price must be greater than 0")
        prices[ticker] = price
    return prices