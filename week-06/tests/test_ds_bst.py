import random

import pytest
from ds.bst import TreeMap
from ds.errors import EmptyError


def build(keys: list[int]) -> TreeMap[int, int]:
    tree: TreeMap[int, int] = TreeMap()
    for key in keys:
        tree.insert(key, key * 10)
    return tree


def test_insert_then_get() -> None:
    tree = build([5, 3, 8])
    assert tree.get(3) == 30
    assert tree.get(99) is None
    assert tree.get(99, -1) == -1
    assert 8 in tree
    assert 9 not in tree


def test_insert_on_an_existing_key_overwrites() -> None:
    tree = build([5])
    tree.insert(5, 123)
    assert tree.get(5) == 123
    assert len(tree) == 1


def test_min_and_max_key() -> None:
    tree = build([50, 30, 70, 20, 80])
    assert tree.min_key() == 20
    assert tree.max_key() == 80


def test_min_and_max_on_an_empty_tree_raise_our_own_error() -> None:
    tree: TreeMap[int, int] = TreeMap()
    with pytest.raises(EmptyError):
        tree.min_key()
    with pytest.raises(EmptyError):
        tree.max_key()


def test_iteration_is_in_key_order_and_can_run_backwards() -> None:
    tree = build([50, 30, 70, 20, 40, 60, 80])
    assert list(tree) == [20, 30, 40, 50, 60, 70, 80]
    assert [key for key, _ in tree.items(descending=True)] == [80, 70, 60, 50, 40, 30, 20]


def test_delete_a_leaf() -> None:
    tree = build([50, 30, 70, 20])
    assert tree.delete(20) is True
    assert list(tree) == [30, 50, 70]


def test_delete_a_node_with_one_child() -> None:
    tree = build([50, 30, 70, 20])  # 30 has only the child 20
    assert tree.delete(30) is True
    assert list(tree) == [20, 50, 70]
    assert tree.height() == 2


def test_delete_a_node_with_two_children_whose_successor_is_its_right_child() -> None:
    tree = build([50, 30, 70, 20, 40, 60, 80])
    assert tree.delete(70) is True  # the next key up is 80, directly on its right
    assert list(tree) == [20, 30, 40, 50, 60, 80]


def test_delete_a_node_with_two_children_whose_successor_is_deeper() -> None:
    tree = build([50, 30, 70, 20, 40, 35, 45])
    assert tree.delete(30) is True  # the next key up is 35, found by going right then left
    assert list(tree) == [20, 35, 40, 45, 50, 70]


def test_delete_the_root_with_two_children() -> None:
    tree = build([50, 30, 70, 20, 40, 60, 80])
    assert tree.delete(50) is True
    assert list(tree) == [20, 30, 40, 60, 70, 80]
    assert tree.get(60) == 600


def test_delete_the_only_key_leaves_an_empty_tree() -> None:
    tree = build([5])
    assert tree.delete(5) is True
    assert len(tree) == 0
    assert tree.height() == 0
    assert list(tree) == []


def test_delete_a_missing_key_returns_false() -> None:
    tree = build([5, 3])
    assert tree.delete(99) is False
    assert len(tree) == 2


def test_matches_a_sorted_list_over_5000_random_inserts_and_deletes() -> None:
    rng = random.Random(3)
    tree: TreeMap[int, int] = TreeMap()
    keys: list[int] = []
    for step in range(5000):
        key = rng.randint(0, 800)
        if rng.random() < 0.6:
            tree.insert(key, step)
            if key not in keys:
                keys.append(key)
                keys.sort()
        else:
            was_there = key in keys
            assert tree.delete(key) == was_there
            if was_there:
                keys.remove(key)
        assert len(tree) == len(keys)
        if keys:
            assert tree.min_key() == keys[0]
            assert tree.max_key() == keys[-1]
    assert list(tree) == keys


def test_5000_sorted_inserts_do_not_raise_recursion_error() -> None:
    tree = build(list(range(5000)))
    assert len(tree) == 5000
    assert tree.get(4321) == 43210
    assert tree.delete(2500) is True
    assert len(list(tree)) == 4999


def test_sorted_inserts_make_a_chain_and_random_inserts_stay_short() -> None:
    chain = build(list(range(5000)))
    assert chain.height() == 5000
    keys = list(range(5000))
    random.Random(1).shuffle(keys)
    shuffled = build(keys)
    assert shuffled.height() < 60