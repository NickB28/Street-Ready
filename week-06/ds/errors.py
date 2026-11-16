"""Errors raised by the data structures, so callers never see IndexError."""


class EmptyError(Exception):
    """Raised when popping or peeking at an empty structure."""