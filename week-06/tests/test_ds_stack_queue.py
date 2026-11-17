import random
from collections import deque

import pytest
from ds.errors import EmptyError
from ds.queue import Queue
from ds.stack import Stack


def test_stack_pops_last_in_first() -> None:
    stack: Stack[int] = Stack()
    stack.push(1)
    stack.push(2)
    stack.push(3)
    assert [stack.pop(), stack.pop(), stack.pop()] == [3, 2, 1]


def test_stack_peek_does_not_remove() -> None:
    stack: Stack[str] = Stack()
    stack.push("a")
    assert stack.peek() == "a"
    assert len(stack) == 1


def test_stack_pop_and_peek_on_empty_raise_our_own_error() -> None:
    stack: Stack[int] = Stack()
    with pytest.raises(EmptyError):
        stack.pop()
    with pytest.raises(EmptyError):
        stack.peek()


def test_queue_dequeues_first_in_first() -> None:
    queue: Queue[int] = Queue()
    for value in (1, 2, 3):
        queue.enqueue(value)
    assert [queue.dequeue(), queue.dequeue(), queue.dequeue()] == [1, 2, 3]


def test_queue_peek_shows_the_oldest_without_removing() -> None:
    queue: Queue[str] = Queue()
    queue.enqueue("a")
    queue.enqueue("b")
    assert queue.peek() == "a"
    assert len(queue) == 2


def test_queue_dequeue_and_peek_on_empty_raise_our_own_error() -> None:
    queue: Queue[int] = Queue()
    with pytest.raises(EmptyError):
        queue.dequeue()
    with pytest.raises(EmptyError):
        queue.peek()


def test_queue_remove_takes_out_an_item_from_the_middle() -> None:
    queue: Queue[str] = Queue()
    queue.enqueue("a")
    middle = queue.enqueue("b")
    queue.enqueue("c")
    queue.remove(middle)
    assert list(queue) == ["a", "c"]
    assert queue.dequeue() == "a"
    assert queue.dequeue() == "c"


def test_queue_matches_collections_deque_over_5000_random_operations() -> None:
    rng = random.Random(5)
    queue: Queue[int] = Queue()
    oracle: deque[int] = deque()
    for step in range(5000):
        if rng.random() < 0.6 or not oracle:
            queue.enqueue(step)
            oracle.append(step)
        else:
            assert queue.dequeue() == oracle.popleft()
        assert len(queue) == len(oracle)
    assert list(queue) == list(oracle)