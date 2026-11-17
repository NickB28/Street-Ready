import random

import pytest
from book import OrderBook
from orders import BookError, Side, Trade


def test_orders_that_do_not_cross_rest_on_the_book() -> None:
    book = OrderBook()
    assert book.add(1, "BUY", 3700, 100) == []
    assert book.add(2, "SELL", 3800, 100) == []
    assert book.best_bid() == 3700
    assert book.best_ask() == 3800


def test_a_crossing_order_trades_at_the_resting_orders_price() -> None:
    book = OrderBook()
    book.add(1, "SELL", 3750, 100)
    assert book.add(2, "BUY", 3800, 100) == [Trade(2, 1, 3750, 100)]
    assert book.best_ask() is None
    assert book.best_bid() is None


def test_partial_fill_leaves_the_rest_of_the_resting_order() -> None:
    book = OrderBook()
    book.add(1, "SELL", 3750, 300)
    assert book.add(2, "BUY", 3750, 100) == [Trade(2, 1, 3750, 100)]
    assert book.levels("SELL", 5) == [(3750, 200)]


def test_unfilled_part_of_an_incoming_order_rests() -> None:
    book = OrderBook()
    book.add(1, "SELL", 3750, 100)
    assert book.add(2, "BUY", 3750, 300) == [Trade(2, 1, 3750, 100)]
    assert book.best_ask() is None
    assert book.levels("BUY", 5) == [(3750, 200)]


def test_sweep_through_three_price_levels() -> None:
    book = OrderBook()
    book.add(1, "SELL", 3740, 300)
    book.add(2, "SELL", 3750, 200)
    book.add(3, "SELL", 3760, 200)
    book.add(4, "SELL", 3770, 100)
    trades = book.add(5, "BUY", 3760, 600)
    assert trades == [Trade(5, 1, 3740, 300), Trade(5, 2, 3750, 200), Trade(5, 3, 3760, 100)]
    assert book.levels("SELL", 5) == [(3760, 100), (3770, 100)]


def test_oldest_order_at_a_price_trades_first() -> None:
    book = OrderBook()
    book.add(1, "SELL", 3750, 100)
    book.add(2, "SELL", 3750, 100)
    assert book.add(3, "BUY", 3750, 100) == [Trade(3, 1, 3750, 100)]
    assert book.add(4, "BUY", 3750, 100) == [Trade(4, 2, 3750, 100)]


def test_better_price_trades_before_an_older_worse_price() -> None:
    book = OrderBook()
    book.add(1, "SELL", 3760, 100)
    book.add(2, "SELL", 3750, 100)
    assert book.add(3, "BUY", 3760, 100) == [Trade(3, 2, 3750, 100)]


def test_selling_mirrors_buying() -> None:
    book = OrderBook()
    book.add(1, "BUY", 3750, 100)
    book.add(2, "BUY", 3740, 100)
    trades = book.add(3, "SELL", 3740, 200)
    assert trades == [Trade(1, 3, 3750, 100), Trade(2, 3, 3740, 100)]


def test_cancel_from_the_middle_of_a_queue() -> None:
    book = OrderBook()
    for order_id in (1, 2, 3):
        book.add(order_id, "SELL", 3750, 100)
    book.cancel(2)
    assert book.add(4, "BUY", 3750, 200) == [Trade(4, 1, 3750, 100), Trade(4, 3, 3750, 100)]


def test_cancel_that_empties_a_level_removes_the_level() -> None:
    book = OrderBook()
    book.add(1, "BUY", 3700, 100)
    book.add(2, "BUY", 3690, 100)
    book.cancel(1)
    assert book.best_bid() == 3690
    assert book.levels("BUY", 5) == [(3690, 100)]


def test_a_level_emptied_by_trading_is_removed_too() -> None:
    book = OrderBook()
    book.add(1, "SELL", 3750, 100)
    book.add(2, "BUY", 3750, 100)
    assert book.best_ask() is None
    assert book.levels("SELL", 5) == []


def test_duplicate_id_is_rejected_even_after_the_order_traded() -> None:
    book = OrderBook()
    book.add(1, "SELL", 3750, 100)
    with pytest.raises(BookError, match="duplicate"):
        book.add(1, "BUY", 3700, 100)
    book.add(2, "BUY", 3750, 100)
    with pytest.raises(BookError, match="duplicate"):
        book.add(2, "BUY", 3700, 100)


def test_cancelling_an_unknown_id_raises() -> None:
    book = OrderBook()
    with pytest.raises(BookError, match="unknown order id 9"):
        book.cancel(9)


def test_cancelling_an_order_that_already_traded_does_nothing() -> None:
    book = OrderBook()
    book.add(1, "SELL", 3750, 100)
    book.add(2, "BUY", 3750, 100)
    book.cancel(1)
    assert book.best_ask() is None


def test_cancelling_twice_raises() -> None:
    book = OrderBook()
    book.add(1, "BUY", 3700, 100)
    book.cancel(1)
    with pytest.raises(BookError, match="already cancelled"):
        book.cancel(1)


def test_levels_add_up_quantity_and_list_the_best_price_first() -> None:
    book = OrderBook()
    book.add(1, "BUY", 3700, 100)
    book.add(2, "BUY", 3700, 200)
    book.add(3, "BUY", 3720, 100)
    book.add(4, "SELL", 3800, 100)
    book.add(5, "SELL", 3790, 300)
    assert book.levels("BUY", 5) == [(3720, 100), (3700, 300)]
    assert book.levels("SELL", 5) == [(3790, 300), (3800, 100)]
    assert book.levels("BUY", 1) == [(3720, 100)]


def test_the_book_is_never_crossed_after_random_commands() -> None:
    rng = random.Random(9)
    book = OrderBook()
    live: list[int] = []
    for order_id in range(1, 3001):
        if live and rng.random() < 0.25:
            book.cancel(live.pop(rng.randrange(len(live))))
        else:
            side: Side = "BUY" if rng.random() < 0.5 else "SELL"
            book.add(order_id, side, 3700 + rng.randint(-6, 6) * 10, rng.randint(1, 8) * 100)
            live.append(order_id)
        bid, ask = book.best_bid(), book.best_ask()
        assert bid is None or ask is None or bid < ask