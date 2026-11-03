"""The Portfolio class: applies trades and keeps positions and realised profit."""

from datetime import date
from decimal import Decimal

from lotbook.errors import OutOfOrderError, OversellError
from lotbook.fees import commission
from lotbook.position import Position
from lotbook.trade import Side, Trade


class Portfolio:
    """Positions built by applying trades in date order."""

    def __init__(self) -> None:
        """Start with no positions and no realised profit."""
        self.positions: dict[str, Position] = {}
        self.realised_pnl = Decimal("0")
        self._last_day: date | None = None

    def apply(self, trade: Trade) -> None:
        """Apply one trade, enforcing date order and the no-oversell rule."""
        if self._last_day is not None and trade.day < self._last_day:
            raise OutOfOrderError(
                f"trade dated {trade.day} is before the last trade on {self._last_day}"
            )
        if trade.side is Side.BUY:
            self._buy(trade)
        else:
            self._sell(trade)
        self._last_day = trade.day

    def _buy(self, trade: Trade) -> None:
        """Add shares to a position. The fee is added to the cost."""
        value = trade.price * trade.quantity
        position = self.positions.get(trade.ticker)
        if position is None:
            position = Position(trade.ticker)
            self.positions[trade.ticker] = position
        position.add(trade.quantity, value + commission(value))

    def _sell(self, trade: Trade) -> None:
        """Remove shares from a position and book the realised profit."""
        position = self.positions.get(trade.ticker)
        if position is None:
            raise OversellError(f"cannot sell {trade.quantity} {trade.ticker}: only 0 held")
        value = trade.price * trade.quantity
        proceeds = value - commission(value)
        cost_removed = position.remove(trade.quantity)
        self.realised_pnl += proceeds - cost_removed
        if position.quantity == 0:
            del self.positions[trade.ticker]