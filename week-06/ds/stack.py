from typing import Generic, TypeVar

from ds.errors import EmptyError

T = TypeVar("T")


class Stack(Generic[T]):
    """Last in, first out, backed by a plain list."""

    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, value: T) -> None:
        self._items.append(value)

    def pop(self) -> T:
        if not self._items:
            raise EmptyError("pop from an empty stack")
        return self._items.pop()

    def peek(self) -> T:
        if not self._items:
            raise EmptyError("peek at an empty stack")
        return self._items[-1]

    def __len__(self) -> int:
        return len(self._items)