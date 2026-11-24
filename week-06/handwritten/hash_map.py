# Written by Claude, not by me. See "How I made this" in week-06/NOTES.md.
from typing import Generic, Iterator, TypeVar

K = TypeVar("K")
V = TypeVar("V")

INITIAL_CAPACITY = 8


class HashMap(Generic[K, V]):
    """Hash map with separate chaining. Starts at 8 buckets and doubles when
    adding a key would push entries / buckets above 0.75."""

    def __init__(self) -> None:
        self._buckets: list[list[tuple[K, V]]] = [[] for _ in range(INITIAL_CAPACITY)]
        self._size = 0

    @property
    def capacity(self) -> int:
        return len(self._buckets)

    @property
    def load_factor(self) -> float:
        return self._size / self.capacity

    def _bucket_for(self, key: K) -> list[tuple[K, V]]:
        return self._buckets[hash(key) % self.capacity]

    def put(self, key: K, value: V) -> None:
        bucket = self._bucket_for(key)
        for position, (existing, _) in enumerate(bucket):
            if existing == key:
                bucket[position] = (key, value)
                return
        # 0.75 is 3 / 4, so compare integers instead of floats.
        if (self._size + 1) * 4 > self.capacity * 3:
            self._resize()
            bucket = self._bucket_for(key)
        bucket.append((key, value))
        self._size += 1

    def _resize(self) -> None:
        new_capacity = self.capacity * 2
        new_buckets: list[list[tuple[K, V]]] = [[] for _ in range(new_capacity)]
        for bucket in self._buckets:
            for key, value in bucket:
                new_buckets[hash(key) % new_capacity].append((key, value))
        self._buckets = new_buckets

    def get(self, key: K, default: V | None = None) -> V | None:
        for existing, value in self._bucket_for(key):
            if existing == key:
                return value
        return default

    def delete(self, key: K) -> bool:
        bucket = self._bucket_for(key)
        for position, (existing, _) in enumerate(bucket):
            if existing == key:
                bucket.pop(position)
                self._size -= 1
                return True
        return False

    def __contains__(self, key: K) -> bool:
        for existing, _ in self._bucket_for(key):
            if existing == key:
                return True
        return False

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[K]:
        for bucket in self._buckets:
            for key, _ in bucket:
                yield key