import random
from collections.abc import Callable
from typing import Any

import pytest
from algos.sorts import heap_sort, insertion_sort, merge_sort, quick_sort

Sorter = Callable[..., list[Any]]
ALL_SORTS = [insertion_sort, merge_sort, quick_sort, heap_sort]
STABLE_SORTS = [insertion_sort, merge_sort]
FAST_SORTS = [merge_sort, quick_sort, heap_sort]


@pytest.mark.parametrize("sort", ALL_SORTS)
def test_matches_sorted_on_200_seeded_random_lists(sort: Sorter) -> None:
    rng = random.Random(2026)
    for _ in range(200):
        data = [rng.randint(-20, 20) for _ in range(rng.randint(0, 300))]
        assert sort(data) == sorted(data)


@pytest.mark.parametrize("sort", ALL_SORTS)
@pytest.mark.parametrize(
    "data",
    [
        [],
        [7],
        [4, 4, 4, 4],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [-3, 5, -10, 0, 5, -3],
    ],
    ids=["empty", "one", "all-equal", "sorted", "reversed", "negatives"],
)
def test_edge_cases(sort: Sorter, data: list[int]) -> None:
    assert sort(data) == sorted(data)


@pytest.mark.parametrize("sort", ALL_SORTS)
def test_input_list_is_not_changed(sort: Sorter) -> None:
    data = [3, 1, 2, 3, 0]
    copy = list(data)
    result = sort(data)
    assert data == copy
    assert result is not data


@pytest.mark.parametrize("sort", ALL_SORTS)
def test_key_function_sorts_by_the_key(sort: Sorter) -> None:
    words = ["pear", "fig", "banana", "kiwi", "apple"]
    assert sort(words, key=len) == sorted(words, key=len)
    assert sort(words, key=lambda w: w[-1]) == sorted(words, key=lambda w: w[-1])


@pytest.mark.parametrize("sort", STABLE_SORTS)
def test_equal_keys_keep_their_original_order(sort: Sorter) -> None:
    rng = random.Random(7)
    records = [(rng.randint(0, 4), index) for index in range(300)]
    result = sort(records, key=lambda record: record[0])
    assert result == sorted(records, key=lambda record: record[0])
    for (key_a, order_a), (key_b, order_b) in zip(result, result[1:]):
        if key_a == key_b:
            assert order_a < order_b


def test_quick_sort_handles_100k_sorted_items_without_recursion_error() -> None:
    data = list(range(100_000))
    assert quick_sort(data) == data


def test_quick_sort_handles_100k_equal_and_reversed_items() -> None:
    assert quick_sort([9] * 100_000) == [9] * 100_000
    assert quick_sort(list(range(100_000, 0, -1))) == list(range(1, 100_001))


@pytest.mark.parametrize("sort", FAST_SORTS)
def test_large_random_list(sort: Sorter) -> None:
    rng = random.Random(5)
    data = [rng.randint(0, 1_000_000) for _ in range(20_000)]
    assert sort(data) == sorted(data)