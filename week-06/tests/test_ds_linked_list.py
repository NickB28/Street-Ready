import pytest
from ds.errors import EmptyError
from ds.linked_list import DoublyLinkedList, Node


def build(values: list[int]) -> tuple[DoublyLinkedList[int], list[Node[int]]]:
    items: DoublyLinkedList[int] = DoublyLinkedList()
    return items, [items.append(value) for value in values]


def test_append_returns_the_node_and_keeps_order() -> None:
    items, nodes = build([1, 2, 3])
    assert list(items) == [1, 2, 3]
    assert nodes[1].value == 2
    assert len(items) == 3


def test_empty_list_has_no_head_or_tail() -> None:
    items: DoublyLinkedList[int] = DoublyLinkedList()
    assert len(items) == 0
    assert items.head is None
    assert items.tail is None
    assert list(items) == []


def test_remove_the_head() -> None:
    items, nodes = build([1, 2, 3])
    items.remove(nodes[0])
    assert list(items) == [2, 3]
    assert items.head is nodes[1]
    assert nodes[1].prev is None


def test_remove_the_tail() -> None:
    items, nodes = build([1, 2, 3])
    items.remove(nodes[2])
    assert list(items) == [1, 2]
    assert items.tail is nodes[1]
    assert nodes[1].next is None


def test_remove_from_the_middle() -> None:
    items, nodes = build([1, 2, 3])
    items.remove(nodes[1])
    assert list(items) == [1, 3]
    assert nodes[0].next is nodes[2]
    assert nodes[2].prev is nodes[0]


def test_remove_the_only_node_empties_the_list() -> None:
    items, nodes = build([7])
    items.remove(nodes[0])
    assert len(items) == 0
    assert items.head is None
    assert items.tail is None


def test_list_still_works_after_it_was_emptied() -> None:
    items, nodes = build([7])
    items.remove(nodes[0])
    items.append(8)
    assert list(items) == [8]
    assert len(items) == 1


def test_popleft_returns_values_oldest_first() -> None:
    items, _ = build([1, 2, 3])
    assert items.popleft() == 1
    assert items.popleft() == 2
    assert len(items) == 1


def test_popleft_on_an_empty_list_raises_our_own_error() -> None:
    items: DoublyLinkedList[int] = DoublyLinkedList()
    with pytest.raises(EmptyError):
        items.popleft()