"""hdbsort command line: range and top queries over HDB resale sales."""

import argparse
import sys
from pathlib import Path

from algos.search import lower_bound, upper_bound
from algos.sorts import merge_sort
from hdb import DataError, Sale, load_sales


def price_of(sale: Sale) -> int:
    """Return a sale's price. Used as the sort key."""
    return sale.resale_price


def money(price: int) -> str:
    """Format a whole-dollar price, for example S$548,000."""
    return f"S${price:,}"


def median_text(prices: list[int]) -> str:
    """Return the exact median of already-sorted prices, showing a half as .5."""
    middle = len(prices) // 2
    if len(prices) % 2:
        return money(prices[middle])
    whole, half = divmod(prices[middle - 1] + prices[middle], 2)
    return money(whole) + (".5" if half else "")


def describe(sale: Sale) -> str:
    """Describe a sale as town, price and month."""
    return f"{sale.town} {money(sale.resale_price)} ({sale.month:%Y-%m})"


def pick(sales: list[Sale], field: str, wanted: str) -> list[Sale]:
    """Return the sales whose town or flat_type matches wanted, ignoring case."""
    wanted = wanted.strip().upper()
    chosen = [s for s in sales if getattr(s, field).upper() == wanted]
    if not chosen:
        known = ", ".join(sorted({getattr(s, field) for s in sales}))
        label = field.replace("_", " ")
        raise DataError(f"unknown {label} {wanted!r} (known: {known})")
    return chosen


def cmd_range(args: argparse.Namespace, sales: list[Sale]) -> list[str]:
    """Report count, median and the cheapest and dearest sale in a price band."""
    if args.min > args.max:
        raise DataError(f"--min {args.min} is above --max {args.max}")
    ranked = merge_sort(pick(sales, "flat_type", args.flat_type), key=price_of)
    prices = [sale.resale_price for sale in ranked]
    # Binary search on the sorted prices finds both edges of the band.
    low, high = lower_bound(prices, args.min), upper_bound(prices, args.max)
    lines = [
        f"Flat type {args.flat_type.strip().upper()}, "
        f"band {money(args.min)} to {money(args.max)}",
        f"Sales in band: {high - low}",
    ]
    if high == low:
        return [*lines, "No sales in this band."]
    return [
        *lines,
        f"Median price: {median_text(prices[low:high])}",
        f"Cheapest: {describe(ranked[low])}",
        f"Dearest: {describe(ranked[high - 1])}",
    ]


def cmd_top(args: argparse.Namespace, sales: list[Sale]) -> list[str]:
    """Report the n most expensive sales in a town."""
    ranked = merge_sort(pick(sales, "town", args.town), key=price_of)
    best = ranked[::-1][: args.n]
    lines = [f"Top {len(best)} sales in {args.town.strip().upper()}"]
    for rank, sale in enumerate(best, 1):
        lines.append(
            f"{rank:>2}. {money(sale.resale_price):>11}  {sale.month:%Y-%m}  "
            f"{sale.flat_type:<10} {sale.floor_area_sqm} sqm"
        )
    return lines


def positive_int(text: str) -> int:
    """Argparse type: an integer of at least 1."""
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a whole number: {text}") from None
    if value < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return value


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(prog="hdb", description="HDB resale queries.")
    sub = parser.add_subparsers(dest="command", required=True)
    rng = sub.add_parser("range", help="count and median of sales in a price band")
    rng.add_argument("data", type=Path, help="resale CSV file")
    rng.add_argument("--flat-type", required=True, help='for example "4 ROOM"')
    rng.add_argument("--min", type=int, default=0, help="lowest price (default 0)")
    rng.add_argument("--max", type=int, default=1_000_000_000, help="highest price")
    rng.set_defaults(func=cmd_range)
    top = sub.add_parser("top", help="the most expensive sales in a town")
    top.add_argument("data", type=Path, help="resale CSV file")
    top.add_argument("--town", required=True, help="for example TAMPINES")
    top.add_argument("-n", type=positive_int, default=5, help="how many (default 5)")
    top.set_defaults(func=cmd_top)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the command line. Exit codes: 0 ok, 1 data error, 2 usage error."""
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as stop:
        return stop.code if isinstance(stop.code, int) else 2
    try:
        sales, skipped = load_sales(args.data)
        if not sales:
            raise DataError(f"no valid sales found in {args.data}")
        if skipped:
            print(f"hdb: skipped {skipped} bad rows in {args.data.name}", file=sys.stderr)
        lines = args.func(args, sales)
    except DataError as err:
        print(f"hdb: error: {err}", file=sys.stderr)
        return 1
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())