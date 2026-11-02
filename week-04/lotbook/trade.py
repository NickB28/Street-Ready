"""The Trade class: one buy or sell of an SGX share."""

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

from lotbook.errors import InvalidTradeError

BOARD_LOT = 100
TICKER_PATTERN = re.compile(r"[A-Z0-9]{2,4}")


class Side(Enum):
    """Whether a trade buys or sells shares."""

    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class Trade:
    """One immutable trade. Its rules are checked when it is created."""

    day: date
    ticker: str
    side: Side
    quantity: int
    price: Decimal

    def __post_init__(self) -> None:
        """Reject a trade that breaks the ticker, board-lot or price rules."""
        if not TICKER_PATTERN.fullmatch(self.ticker):
            raise InvalidTradeError(
                f"ticker must be 2-4 uppercase letters or digits: {self.ticker!r}"
            )
        if self.quantity <= 0 or self.quantity % BOARD_LOT != 0:
            raise InvalidTradeError(
                f"quantity must be a positive multiple of {BOARD_LOT}: {self.quantity}"
            )
        if not self.price.is_finite() or self.price <= 0:
            raise InvalidTradeError(f"price must be greater than 0: {self.price}")