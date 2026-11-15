from typing import Generic, TypeVar

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
    