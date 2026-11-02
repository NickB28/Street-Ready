"""The fee rule for lotbook. It is made up for this task, not a real broker's."""

from decimal import ROUND_HALF_UP, Decimal

COMMISSION_RATE = Decimal("0.0012")
MIN_COMMISSION = Decimal("10.00")
CENT = Decimal("0.01")


def commission(value: Decimal) -> Decimal:
    """Return the fee on a trade worth value: 0.12%, with a S$10.00 minimum."""
    fee = (value * COMMISSION_RATE).quantize(CENT, rounding=ROUND_HALF_UP)
    return max(fee, MIN_COMMISSION)