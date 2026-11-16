from typing import Generic, Iterator, TypeVar

from ds.errors import EmptyError
from ds.linked_list import DoublyLinkedList, Node

T = TypeVar("T")


class Queue(Generic[T]):
    """First in, first out, built on the doubly linked list.

    enqueue returns the node, and remove(node) takes any waiting item out in O(1);
    the order book uses these to cancel an order from the middle of a price level.
    """

    def __init__(self) -> None:
        self._list: DoublyLinkedList[T] = DoublyLinkedList()

    def enqueue(self, value: T) -> Node[T]:
        return self._list.append(value)

    def dequeue(self) -> T:
        if len(self._list) == 0:
            raise EmptyError("dequeue from an empty queue")
        return self._list.popleft()

    def peek(self) -> T:
        node = self._list.head
        if node is None:
            raise EmptyError("peek at an empty queue")
        return node.value

    def remove(self, node: Node[T]) -> None:
        self._list.remove(node)

    def __len__(self) -> int:
        return len(self._list)

    def __iter__(self) -> Iterator[T]:
        return iter(self._list)