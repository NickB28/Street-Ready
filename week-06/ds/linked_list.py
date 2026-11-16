from typing import Generic, Iterator, TypeVar

from ds.errors import EmptyError

T = TypeVar("T")


class Node(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value
        self.prev: Node[T] | None = None
        self.next: Node[T] | None = None


class DoublyLinkedList(Generic[T]):
    def __init__(self) -> None:
        self.head: Node[T] | None = None
        self.tail: Node[T] | None = None
        self.size: int = 0

    def append(self, value: T) -> Node[T]:
        node = Node(value)
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            assert self.tail is not None
            self.tail.next = node
            node.prev = self.tail
            self.tail = node
        self.size += 1
        return node

    def __len__(self) -> int:
        return self.size

    def __iter__(self) -> Iterator[T]:
        current = self.head
        while current is not None:
            yield current.value
            current = current.next

    def remove(self, node: Node[T]) -> None:
        """Unlink a node in O(1). The node must currently be in this list."""
        if node.prev is None:
            self.head = node.next
        else:
            node.prev.next = node.next
        if node.next is None:
            self.tail = node.prev
        else:
            node.next.prev = node.prev
        node.prev = None
        node.next = None
        self.size -= 1

    def popleft(self) -> T:
        node = self.head
        if node is None:
            raise EmptyError("popleft from an empty list")
        self.remove(node)
        return node.value