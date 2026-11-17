"""Command line for sgxbook: replay a CSV of orders and print the result.

    python week-06/book_cli.py replay week-06/data/orders.csv

Exit codes: 0 ok, 1 data error (named by file and line), 2 usage.
"""

import argparse
import csv
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from orders import BookError, Side, Trade

BOARD_LOT = 100
TOP_LEVELS = 5


class CommandError(Exception):
    """A bad line in the input file; the message already names file and line."""


class Book(Protocol):
    """What the CLI needs from the order book (book.py provides it)."""

    def add(self, order_id: int, side: Side, price: int, qty: int) -> list[Trade]: ...

    def cancel(self, order_id: int) -> None: ...

    def best_bid(self) -> int | None: ...

    def best_ask(self) -> int | None: ...

    def levels(self, side: Side, n: int) -> list[tuple[int, int]]:
        """Best-first (price, total quantity) for the top n levels of one side."""
        ...


@dataclass(frozen=True)
class Command:
    kind: str  # "ADD" or "CANCEL"
    order_id: int
    side: Side | None = None
    price: int = 0
    qty: int = 0


def whole_number(text: str, what: str) -> int:
    """Parse digits only: no signs, no decimals, no spaces inside."""
    text = text.strip()
    if not text.isascii() or not text.isdigit():
        raise ValueError(f"{what} must be a whole number, got {text!r}")
    return int(text)


def parse_command(fields: Sequence[str]) -> Command:
    """Turn one CSV row into a Command, or raise ValueError saying what is wrong."""
    kind = fields[0].strip().upper() if fields else ""
    if kind == "CANCEL":
        if len(fields) != 2:
            raise ValueError(f"CANCEL needs 2 fields, got {len(fields)}")
        return Command("CANCEL", whole_number(fields[1], "order id"))
    if kind == "ADD":
        if len(fields) != 5:
            raise ValueError(f"ADD needs 5 fields, got {len(fields)}")
        order_id = whole_number(fields[1], "order id")
        side = fields[2].strip().upper()
        if side not in ("BUY", "SELL"):
            raise ValueError(f"side must be BUY or SELL, got {fields[2].strip()!r}")
        price = whole_number(fields[3], "price (cents)")
        if price <= 0:
            raise ValueError("price must be above 0")
        qty = whole_number(fields[4], "quantity")
        if qty <= 0 or qty % BOARD_LOT != 0:
            raise ValueError(f"quantity must be a positive multiple of {BOARD_LOT}, got {qty}")
        return Command("ADD", order_id, "BUY" if side == "BUY" else "SELL", price, qty)
    raise ValueError(f"unknown command {kind!r} (expected ADD or CANCEL)")


def dollars(cents: int) -> str:
    """Integer cents to text, e.g. 3750 -> '37.50'. No floats anywhere."""
    whole, rest = divmod(cents, 100)
    return f"{whole}.{rest:02d}"


def replay(path: Path, book: Book) -> list[Trade]:
    """Run every command in the file against the book and return all trades."""
    trades: list[Trade] = []
    try:
        handle = path.open(newline="", encoding="utf-8-sig")
    except OSError as error:
        raise CommandError(f"{path}: cannot read file: {error.strerror or error}") from error
    with handle:
        for line_no, fields in enumerate(csv.reader(handle), start=1):
            if not fields or all(not field.strip() for field in fields):
                continue
            try:
                command = parse_command(fields)
                if command.kind == "CANCEL":
                    book.cancel(command.order_id)
                else:
                    assert command.side is not None
                    trades.extend(
                        book.add(command.order_id, command.side, command.price, command.qty)
                    )
            except (ValueError, BookError) as error:
                raise CommandError(f"{path}:{line_no}: {error}") from error
    return trades


def format_levels(title: str, levels: list[tuple[int, int]]) -> list[str]:
    lines = [title]
    if not levels:
        lines.append("  (empty)")
    for price, qty in levels:
        lines.append(f"  S${dollars(price):>8}  {qty:>8} shares")
    return lines


def report(trades: list[Trade], book: Book) -> str:
    lines = [f"Trades ({len(trades)}):"]
    for trade in trades:
        lines.append(
            f"  buy #{trade.buy_id} sell #{trade.sell_id} "
            f"S${dollars(trade.price)} x {trade.qty}"
        )
    bid, ask = book.best_bid(), book.best_ask()
    lines.append(f"Best bid: {'none' if bid is None else 'S$' + dollars(bid)}")
    lines.append(f"Best ask: {'none' if ask is None else 'S$' + dollars(ask)}")
    lines.extend(format_levels(f"Top {TOP_LEVELS} bids:", book.levels("BUY", TOP_LEVELS)))
    lines.extend(format_levels(f"Top {TOP_LEVELS} asks:", book.levels("SELL", TOP_LEVELS)))
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="book_cli", description="sgxbook order book")
    sub = parser.add_subparsers(dest="command", required=True)
    replay_cmd = sub.add_parser("replay", help="replay a CSV of ADD/CANCEL commands")
    replay_cmd.add_argument("file", type=Path)
    return parser


def main(argv: Sequence[str] | None = None, book: Book | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as error:
        return int(error.code) if isinstance(error.code, int) else 2
    if book is None:
        from book import OrderBook  # imported late so tests can pass a stub book

        book = OrderBook()
    try:
        trades = replay(args.file, book)
    except CommandError as error:
        print(f"book_cli: error: {error}", file=sys.stderr)
        return 1
    print(report(trades, book))
    return 0


if __name__ == "__main__":
    sys.exit(main())