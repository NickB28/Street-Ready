import random

from ds.hash_map import HashMap


class AlwaysCollide:
    """A key whose hash is always 42, so every key lands in the same bucket."""

    def __init__(self, number: int) -> None:
        self.number = number

    def __hash__(self) -> int:
        return 42

    def __eq__(self, other: object) -> bool:
        return isinstance(other, AlwaysCollide) and other.number == self.number


def test_put_then_get() -> None:
    table: HashMap[str, int] = HashMap()
    table.put("a", 1)
    assert table.get("a") == 1


def test_get_returns_the_default_for_a_missing_key() -> None:
    table: HashMap[str, int] = HashMap()
    assert table.get("missing") is None
    assert table.get("missing", -1) == -1


def test_put_on_an_existing_key_overwrites_without_growing() -> None:
    table: HashMap[str, int] = HashMap()
    table.put("a", 1)
    table.put("a", 2)
    assert table.get("a") == 2
    assert len(table) == 1


def test_delete_removes_the_key_and_says_whether_it_was_there() -> None:
    table: HashMap[str, int] = HashMap()
    table.put("a", 1)
    assert table.delete("a") is True
    assert table.delete("a") is False
    assert "a" not in table
    assert len(table) == 0


def test_contains_is_true_only_for_stored_keys() -> None:
    table: HashMap[int, int] = HashMap()
    table.put(1, 10)
    assert 1 in table
    assert 2 not in table


def test_a_new_map_starts_with_8_buckets() -> None:
    table: HashMap[int, int] = HashMap()
    assert table.capacity == 8
    assert table.load_factor == 0


def test_resize_doubles_the_buckets_when_load_would_pass_three_quarters() -> None:
    table: HashMap[int, int] = HashMap()
    for key in range(6):  # 6 of 8 buckets is exactly 0.75, which is allowed
        table.put(key, key)
    assert table.capacity == 8
    table.put(6, 6)  # the 7th key would make 7/8, so the map doubles first
    assert table.capacity == 16
    for key in range(7, 12):
        table.put(key, key)
    assert table.capacity == 16  # 12 of 16 is exactly 0.75
    table.put(12, 12)
    assert table.capacity == 32


def test_load_factor_never_goes_above_three_quarters() -> None:
    table: HashMap[int, int] = HashMap()
    for key in range(500):
        table.put(key, key)
        assert table.load_factor <= 0.75


def test_resize_keeps_every_key_findable() -> None:
    table: HashMap[int, int] = HashMap()
    for key in range(200):
        table.put(key, key * 2)
    assert table.capacity > 8
    assert len(table) == 200
    assert all(table.get(key) == key * 2 for key in range(200))


def test_correct_when_every_key_collides() -> None:
    table: HashMap[AlwaysCollide, int] = HashMap()
    for number in range(50):
        table.put(AlwaysCollide(number), number)
    assert len(table) == 50
    assert all(table.get(AlwaysCollide(number)) == number for number in range(50))
    assert AlwaysCollide(7) in table
    assert AlwaysCollide(99) not in table
    assert table.delete(AlwaysCollide(7)) is True
    assert AlwaysCollide(7) not in table
    assert len(table) == 49


def test_iteration_yields_each_key_once() -> None:
    table: HashMap[int, int] = HashMap()
    for key in range(30):
        table.put(key, key)
    assert sorted(table) == list(range(30))


def test_matches_a_dict_over_10000_random_operations() -> None:
    rng = random.Random(11)
    table: HashMap[int, int] = HashMap()
    oracle: dict[int, int] = {}
    for step in range(10_000):
        key = rng.randint(0, 300)
        choice = rng.random()
        if choice < 0.5:
            table.put(key, step)
            oracle[key] = step
        elif choice < 0.8:
            assert table.get(key) == oracle.get(key)
        else:
            assert table.delete(key) == (oracle.pop(key, None) is not None)
        assert len(table) == len(oracle)
        assert (key in table) == (key in oracle)
    assert sorted(table) == sorted(oracle)