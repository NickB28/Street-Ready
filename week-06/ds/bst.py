from typing import Any, Generic, Iterator, Protocol, TypeVar

from ds.errors import EmptyError
from ds.stack import Stack


class _Comparable(Protocol):
    def __lt__(self, other: Any, /) -> bool: ...


K = TypeVar("K", bound=_Comparable)
V = TypeVar("V")


class _Node(Generic[K, V]):
    def __init__(self, key: K, value: V) -> None:
        self.key = key
        self.value = value
        self.left: _Node[K, V] | None = None
        self.right: _Node[K, V] | None = None


class TreeMap(Generic[K, V]):
    """Binary search tree keyed by K, written with loops only (no recursion).

    Keys are compared with "<" alone: two keys are equal when neither is below the
    other. The tree is not balanced, so keys added in ascending order make a long chain
    (see height()). Every method is iterative, so a chain of any length cannot raise
    RecursionError.
    """

    def __init__(self) -> None:
        self._root: _Node[K, V] | None = None
        self._size = 0

    def insert(self, key: K, value: V) -> None:
        """Add a key, or overwrite the value if the key is already there."""
        if self._root is None:
            self._root = _Node(key, value)
            self._size = 1
            return
        node = self._root
        while True:
            if key < node.key:
                if node.left is None:
                    node.left = _Node(key, value)
                    self._size += 1
                    return
                node = node.left
            elif node.key < key:
                if node.right is None:
                    node.right = _Node(key, value)
                    self._size += 1
                    return
                node = node.right
            else:
                node.value = value
                return

    def get(self, key: K, default: V | None = None) -> V | None:
        node = self._root
        while node is not None:
            if key < node.key:
                node = node.left
            elif node.key < key:
                node = node.right
            else:
                return node.value
        return default

    def __contains__(self, key: K) -> bool:
        node = self._root
        while node is not None:
            if key < node.key:
                node = node.left
            elif node.key < key:
                node = node.right
            else:
                return True
        return False

    def delete(self, key: K) -> bool:
        """Remove a key. Returns True if it was there, False if not."""
        parent: _Node[K, V] | None = None
        node = self._root
        while node is not None and (key < node.key or node.key < key):
            parent = node
            node = node.left if key < node.key else node.right
        if node is None:
            return False
        if node.left is not None and node.right is not None:
            # Two children: copy in the next key up (the smallest key on the right),
            # then remove that smaller node instead, which has no left child.
            successor_parent = node
            successor = node.right
            while successor.left is not None:
                successor_parent = successor
                successor = successor.left
            node.key = successor.key
            node.value = successor.value
            parent = successor_parent
            node = successor
        # Zero or one child: the node's only child (or nothing) takes its place.
        child = node.left if node.left is not None else node.right
        if parent is None:
            self._root = child
        elif parent.left is node:
            parent.left = child
        else:
            parent.right = child
        self._size -= 1
        return True

    def min_key(self) -> K:
        node = self._root
        if node is None:
            raise EmptyError("min_key of an empty tree")
        while node.left is not None:
            node = node.left
        return node.key

    def max_key(self) -> K:
        node = self._root
        if node is None:
            raise EmptyError("max_key of an empty tree")
        while node.right is not None:
            node = node.right
        return node.key

    def items(self, descending: bool = False) -> Iterator[tuple[K, V]]:
        """Yield (key, value) in key order, or highest first if descending."""
        pending: Stack[_Node[K, V]] = Stack()
        node = self._root
        while node is not None or len(pending) > 0:
            while node is not None:
                pending.push(node)
                node = node.right if descending else node.left
            node = pending.pop()
            yield node.key, node.value
            node = node.left if descending else node.right

    def __iter__(self) -> Iterator[K]:
        for key, _ in self.items():
            yield key

    def __len__(self) -> int:
        return self._size

    def height(self) -> int:
        """Number of nodes on the longest path from the root down (empty tree: 0)."""
        deepest = 0
        pending: Stack[tuple[_Node[K, V], int]] = Stack()
        if self._root is not None:
            pending.push((self._root, 1))
        while len(pending) > 0:
            node, depth = pending.pop()
            if depth > deepest:
                deepest = depth
            if node.left is not None:
                pending.push((node.left, depth + 1))
            if node.right is not None:
                pending.push((node.right, depth + 1))
        return deepest