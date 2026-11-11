import bisect
import random

from algos.search import lower_bound, upper_bound

DATA = [1, 3, 3, 3, 5, 8, 8, 13]


def test_lower_and_upper_bound_match_bisect_for_many_values() -> None:
    for x in range(-2, 16):
        assert lower_bound(DATA, x) == bisect.bisect_left(DATA, x)
        assert upper_bound(DATA, x) == bisect.bisect_right(DATA, x)


def test_value_below_the_minimum_and_above_the_maximum() -> None:
    assert lower_bound(DATA, 0) == 0
    assert upper_bound(DATA, 0) == 0
    assert lower_bound(DATA, 99) == len(DATA)
    assert upper_bound(DATA, 99) == len(DATA)


def test_absent_value_gives_the_same_index_for_both() -> None:
    assert lower_bound(DATA, 4) == upper_bound(DATA, 4) == 4


def test_repeated_value_spans_its_whole_run() -> None:
    low, high = lower_bound(DATA, 3), upper_bound(DATA, 3)
    assert (low, high) == (1, 4)
    assert high - low == DATA.count(3)


def test_empty_list() -> None:
    assert lower_bound([], 5) == 0
    assert upper_bound([], 5) == 0


def test_key_function_and_random_lists_match_bisect() -> None:
    rng = random.Random(11)
    for _ in range(200):
        data = sorted(rng.randint(0, 30) for _ in range(rng.randint(0, 60)))
        x = rng.randint(-2, 32)
        assert lower_bound(data, x) == bisect.bisect_left(data, x)
        assert upper_bound(data, x) == bisect.bisect_right(data, x)
    pairs = [("a", 1), ("b", 2), ("c", 2), ("d", 4)]
    assert lower_bound(pairs, 2, key=lambda p: p[1]) == 1
    assert upper_bound(pairs, 2, key=lambda p: p[1]) == 3