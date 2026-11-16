from typing import Generic, Iterator, TypeVar

K = TypeVar("K")
V = TypeVar("V")

INITIAL_CAPACITY = 8


class _Entry(Generic[K, V]):
    def __init__(self, key: K, value: V) -> None:
        self.key = key
        self.value = value


class HashMap(Generic[K, V]):
    """Hash map using separate chaining: each bucket is a small list of entries.

    Starts with 8 buckets and doubles whenever adding a key would push the load
    factor (entries / buckets) above 0.75.
    """

    def __init__(self) -> None:
        self._buckets: list[list[_Entry[K, V]]] = [[] for _ in range(INITIAL_CAPACITY)]
        self._size = 0

    @property
    def capacity(self) -> int:
        return len(self._buckets)

    @property
    def load_factor(self) -> float:
        return self._size / self.capacity

    def _bucket_for(self, key: K) -> list[_Entry[K, V]]:
        return self._buckets[hash(key) % self.capacity]

    def put(self, key: K, value: V) -> None:
        bucket = self._bucket_for(key)
        for entry in bucket:
            if entry.key == key:
                entry.value = value
                return
        # 0.75 as the integers 3 / 4, so the check uses no floating point.
        if (self._size + 1) * 4 > self.capacity * 3:
            self._resize()
            bucket = self._bucket_for(key)
        bucket.append(_Entry(key, value))
        self._size += 1

    def _resize(self) -> None:
        new_capacity = self.capacity * 2
        new_buckets: list[list[_Entry[K, V]]] = [[] for _ in range(new_capacity)]
        for bucket in self._buckets:
            for entry in bucket:
                new_buckets[hash(entry.key) % new_capacity].append(entry)
        self._buckets = new_buckets

    def get(self, key: K, default: V | None = None) -> V | None:
        for entry in self._bucket_for(key):
            if entry.key == key:
                return entry.value
        return default

    def delete(self, key: K) -> bool:
        """Remove a key. Returns True if it was there, False if not."""
        bucket = self._bucket_for(key)
        for position, entry in enumerate(bucket):
            if entry.key == key:
                bucket.pop(position)
                self._size -= 1
                return True
        return False

    def __contains__(self, key: K) -> bool:
        for entry in self._bucket_for(key):
            if entry.key == key:
                return True
        return False

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[K]:
        for bucket in self._buckets:
            for entry in bucket:
                yield entry.key