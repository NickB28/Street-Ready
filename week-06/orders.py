"""Shared types for the order book: sides, trades and the book's error."""

from dataclasses import dataclass
from typing import Literal

Side = Literal["BUY", "SELL"]


class BookError(Exception):
    """A command the book cannot accept (duplicate id, unknown cancel, ...)."""


@dataclass(frozen=True)
class Trade:
    buy_id: int
    sell_id: int
    price: int  # integer cents, the resting order's price
    qty: int