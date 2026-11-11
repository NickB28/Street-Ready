"""Four sorting algorithms written from scratch.

All four take a list and an optional key function, and return a NEW sorted
list. The input list is never changed. Each element's key is computed once.
"""

from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")
KeyFunc = Callable[[T], Any]
Pair = tuple[Any, T]


def _decorate(items: list[T], key: KeyFunc[T] | None) -> list[Pair[T]]:
    """Pair every item with its key, so the key function runs once per item."""
    if key is None:
        return [(item, item) for item in items]
    return [(key(item), item) for item in items]


def _undecorate(pairs: list[Pair[T]]) -> list[T]:
    """Drop the keys and return just the items."""
    return [item for _, item in pairs]


def insertion_sort(items: list[T], key: KeyFunc[T] | None = None) -> list[T]:
    """Return a new sorted list using insertion sort. Stable."""
    pairs = _decorate(items, key)
    for i in range(1, len(pairs)):
        current = pairs[i]
        j = i - 1
        # Strict ">" means equal keys are never passed, which keeps it stable.
        while j >= 0 and pairs[j][0] > current[0]:
            pairs[j + 1] = pairs[j]
            j -= 1
        pairs[j + 1] = current
    return _undecorate(pairs)


def _merge(left: list[Pair[T]], right: list[Pair[T]]) -> list[Pair[T]]:
    """Merge two sorted lists into one sorted list."""
    merged: list[Pair[T]] = []
    i = j = 0
    while i < len(left) and j < len(right):
        # "<=" takes from the left on a tie, which keeps the merge stable.
        if left[i][0] <= right[j][0]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def _merge_sort_pairs(pairs: list[Pair[T]]) -> list[Pair[T]]:
    """Recursively split in half, sort each half, then merge."""
    if len(pairs) <= 1:
        return pairs
    middle = len(pairs) // 2
    return _merge(_merge_sort_pairs(pairs[:middle]), _merge_sort_pairs(pairs[middle:]))


def merge_sort(items: list[T], key: KeyFunc[T] | None = None) -> list[T]:
    """Return a new sorted list using merge sort. Stable."""
    return _undecorate(_merge_sort_pairs(_decorate(items, key)))


def _median_of_three(pairs: list[Pair[T]], lo: int, hi: int) -> Any:
    """Return the median of the first, middle and last keys, to use as pivot."""
    a, b, c = pairs[lo][0], pairs[(lo + hi) // 2][0], pairs[hi][0]
    if a <= b <= c or c <= b <= a:
        return b
    if b <= a <= c or c <= a <= b:
        return a
    return c


def _partition(pairs: list[Pair[T]], lo: int, hi: int, pivot: Any) -> tuple[int, int]:
    """Three-way partition of pairs[lo..hi] around pivot.

    Afterwards: keys in lo..lt-1 are < pivot, lt..gt are == pivot,
    and gt+1..hi are > pivot. Returns (lt, gt).
    """
    lt, i, gt = lo, lo, hi
    while i <= gt:
        k = pairs[i][0]
        if k < pivot:
            pairs[lt], pairs[i] = pairs[i], pairs[lt]
            lt += 1
            i += 1
        elif k > pivot:
            pairs[i], pairs[gt] = pairs[gt], pairs[i]
            gt -= 1
        else:
            i += 1
    return lt, gt


def quick_sort(items: list[T], key: KeyFunc[T] | None = None) -> list[T]:
    """Return a new sorted list using quicksort. Not stable.

    Median-of-three pivot plus a three-way partition keeps sorted and
    all-equal input fast. Recursion is replaced by a stack, and the larger
    part is always pushed while the smaller is handled next, so the stack
    never holds more than about log2(n) ranges.
    """
    pairs = _decorate(items, key)
    stack = [(0, len(pairs) - 1)]
    while stack:
        lo, hi = stack.pop()
        while lo < hi:
            lt, gt = _partition(pairs, lo, hi, _median_of_three(pairs, lo, hi))
            if lt - lo < hi - gt:
                stack.append((gt + 1, hi))
                hi = lt - 1
            else:
                stack.append((lo, lt - 1))
                lo = gt + 1
    return _undecorate(pairs)


def _sift_down(pairs: list[Pair[T]], root: int, end: int) -> None:
    """Push pairs[root] down until the max-heap rule holds in pairs[:end]."""
    while True:
        child = 2 * root + 1
        if child >= end:
            return
        if child + 1 < end and pairs[child][0] < pairs[child + 1][0]:
            child += 1
        if pairs[root][0] >= pairs[child][0]:
            return
        pairs[root], pairs[child] = pairs[child], pairs[root]
        root = child


def heap_sort(items: list[T], key: KeyFunc[T] | None = None) -> list[T]:
    """Return a new sorted list using heap sort. Not stable."""
    pairs = _decorate(items, key)
    size = len(pairs)
    for start in range(size // 2 - 1, -1, -1):
        _sift_down(pairs, start, size)
    for end in range(size - 1, 0, -1):
        pairs[0], pairs[end] = pairs[end], pairs[0]
        _sift_down(pairs, 0, end)
    return _undecorate(pairs)