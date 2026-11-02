"""The Position class: the shares held in one ticker and what they cost."""

from decimal import Decimal

from lotbook.errors import OversellError


class Position:
    """Shares held in one ticker, with the total cost paid for them."""

    def __init__(self, ticker: str) -> None:
        """Start an empty position for ticker."""
        self.ticker = ticker
        self.quantity = 0
        self.total_cost = Decimal("0")

    @property
    def average_cost(self) -> Decimal:
        """Return the average cost per share, or 0 if nothing is held."""
        if self.quantity == 0:
            return Decimal("0")
        return self.total_cost / self.quantity

    def add(self, quantity: int, cost: Decimal) -> None:
        """Add bought shares and the cost paid for them, fees included."""
        self.quantity += quantity
        self.total_cost += cost

    def remove(self, quantity: int) -> Decimal:
        """Remove sold shares and return the part of the cost they carried."""
        if quantity > self.quantity:
            raise OversellError(
                f"cannot sell {quantity} {self.ticker}: only {self.quantity} held"
            )
        cost_removed = self.total_cost * quantity / self.quantity
        self.quantity -= quantity
        self.total_cost -= cost_removed
        return cost_removed