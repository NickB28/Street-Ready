"""Exceptions raised by the lotbook domain model."""


class LotbookError(Exception):
    """Base class for every error lotbook raises on purpose."""


class InvalidTradeError(LotbookError):
    """A trade breaks a rule when it is created (lot size, price, ticker)."""


class OversellError(LotbookError):
    """A sell is bigger than the shares held."""


class OutOfOrderError(LotbookError):
    """A trade is dated earlier than one already applied."""