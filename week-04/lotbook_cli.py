"""lotbook command line: report positions and profit from two CSV files."""

import argparse
import csv
import sys
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

from lotbook.errors import LotbookError
from lotbook.portfolio import Portfolio
from lotbook.position import Position
from lotbook.trade import Side, Trade

CENT = Decimal("0.01")
FOUR_PLACES = Decimal("0.0001")
HEADER = (
    f"{'TICKER':<8}{'QTY':>8}{'AVG COST':>12}{'LAST':>10}{'VALUE':>14}{'UNREALISED':>14}"
)


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


def money(value: Decimal) -> str:
    """Format value to 2 decimal places, rounding half up."""
    return str(value.quantize(CENT, rounding=ROUND_HALF_UP))


def format_position(position: Position, price: Decimal) -> str:
    """Format one report line for a position at the given last price."""
    average = str(position.average_cost.quantize(FOUR_PLACES, rounding=ROUND_HALF_UP))
    value = price * position.quantity
    unrealised = value - position.total_cost
    return (
        f"{position.ticker:<8}{position.quantity:>8}{average:>12}"
        f"{money(price):>10}{money(value):>14}{money(unrealised):>14}"
    )


def build_report(portfolio: Portfolio, prices: dict[str, Decimal]) -> list[str]:
    """Return the report lines: one per position, then totals and realised profit."""
    lines = [HEADER]
    value_total = Decimal("0")
    cost_total = Decimal("0")
    for ticker in sorted(portfolio.positions):
        if ticker not in prices:
            raise DataError(f"no price for {ticker} in the prices file")
        position = portfolio.positions[ticker]
        lines.append(format_position(position, prices[ticker]))
        value_total += prices[ticker] * position.quantity
        cost_total += position.total_cost
    unrealised_total = value_total - cost_total
    lines.append(
        f"{'TOTAL':<8}{'':30}{money(value_total):>14}{money(unrealised_total):>14}"
    )
    lines.append(f"Realised P&L: {money(portfolio.realised_pnl)}")
    return lines


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(prog="lotbook", description="SGX portfolio ledger.")
    sub = parser.add_subparsers(dest="command", required=True)
    report = sub.add_parser("report", help="print positions and profit")
    report.add_argument("trades", type=Path, help="trades CSV file")
    report.add_argument("--prices", type=Path, required=True, help="prices CSV file")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the command line. Exit codes: 0 ok, 1 data error, 2 usage error."""
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as stop:
        return stop.code if isinstance(stop.code, int) else 2
    try:
        portfolio = load_portfolio(args.trades)
        lines = build_report(portfolio, read_prices(args.prices))
    except DataError as err:
        print(f"lotbook: error: {err}", file=sys.stderr)
        return 1
    except ArithmeticError:
        print("lotbook: error: a number is too large", file=sys.stderr)
        return 1
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())