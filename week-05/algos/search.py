"""Binary search written by hand: lower_bound and upper_bound.

Both work on a list that is already sorted by the key (or by the items
themselves when no key is given). Each does at most about log2(n) + 1 steps.
"""

from collections.abc import Sequence
from typing import Any, TypeVar

from algos.sorts import KeyFunc

T = TypeVar("T")


def lower_bound(items: Sequence[T], x: Any, key: KeyFunc[T] | None = None) -> int:
    """Return the first index whose key is >= x (len(items) if there is none)."""
    lo, hi = 0, len(items)
    # Invariant: every index < lo has key < x, and every index >= hi has key >= x.
    # The answer is always in lo..hi. Each pass shrinks hi - lo, so the loop ends.
    while lo < hi:
        mid = (lo + hi) // 2
        value = items[mid] if key is None else key(items[mid])
        if value < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def upper_bound(items: Sequence[T], x: Any, key: KeyFunc[T] | None = None) -> int:
    """Return the first index whose key is > x (len(items) if there is none)."""
    lo, hi = 0, len(items)
    # Invariant: every index < lo has key <= x, and every index >= hi has key > x.
    while lo < hi:
        mid = (lo + hi) // 2
        value = items[mid] if key is None else key(items[mid])
        if value <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo
