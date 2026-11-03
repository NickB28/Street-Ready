from dataclasses import FrozenInstanceError
from datetime import date
from decimal import Decimal

import pytest
from lotbook.errors import (
    InvalidTradeError,
    LotbookError,
    OutOfOrderError,
    OversellError,
)
from lotbook.fees import commission
from lotbook.portfolio import Portfolio
from lotbook.trade import Side, Trade


def make_trade(
    day: int, side: Side, quantity: int, price: str, ticker: str = "D05"
) -> Trade:
    """Build a trade in October 2026 on the given day of the month."""
    return Trade(date(2026, 10, day), ticker, side, quantity, Decimal(price))


def hand_example() -> Portfolio:
    """Return a portfolio after the two buys of the hand-worked example."""
    portfolio = Portfolio()
    portfolio.apply(make_trade(1, Side.BUY, 300, "35.20"))
    portfolio.apply(make_trade(2, Side.BUY, 200, "36.10"))
    return portfolio


def test_board_lot_rejects_150_shares() -> None:
    with pytest.raises(InvalidTradeError, match="multiple of 100"):
        make_trade(1, Side.BUY, 150, "35.20")


@pytest.mark.parametrize("quantity", [0, -100, 99, 150])
def test_bad_quantities_are_rejected(quantity: int) -> None:
    with pytest.raises(InvalidTradeError, match="positive multiple of 100"):
        make_trade(1, Side.BUY, quantity, "35.20")


@pytest.mark.parametrize("price", ["0", "-1.00", "NaN"])
def test_price_must_be_above_zero(price: str) -> None:
    with pytest.raises(InvalidTradeError, match="greater than 0"):
        make_trade(1, Side.BUY, 100, price)


@pytest.mark.parametrize("ticker", ["d05", "D", "ABCDE", "D-5", ""])
def test_bad_tickers_are_rejected(ticker: str) -> None:
    with pytest.raises(InvalidTradeError, match="ticker"):
        make_trade(1, Side.BUY, 100, "35.20", ticker=ticker)


def test_trade_is_immutable() -> None:
    trade = make_trade(1, Side.BUY, 100, "35.20")
    with pytest.raises(FrozenInstanceError):
        setattr(trade, "quantity", 200)


def test_all_errors_share_one_base_class() -> None:
    for error in (InvalidTradeError, OversellError, OutOfOrderError):
        assert issubclass(error, LotbookError)


def test_average_cost_after_two_buys() -> None:
    position = hand_example().positions["D05"]
    assert position.quantity == 500
    assert position.total_cost == Decimal("17802.67")
    assert position.average_cost == Decimal("35.60534")


def test_partial_sell_books_the_hand_worked_profit() -> None:
    portfolio = hand_example()
    portfolio.apply(make_trade(3, Side.SELL, 400, "37.00"))
    position = portfolio.positions["D05"]
    assert portfolio.realised_pnl == Decimal("540.104")
    assert position.quantity == 100
    assert position.total_cost == Decimal("3560.534")


def test_small_trade_pays_the_minimum_commission() -> None:
    assert commission(Decimal("7220.00")) == Decimal("10.00")
    portfolio = Portfolio()
    portfolio.apply(make_trade(1, Side.BUY, 100, "35.20"))
    assert portfolio.positions["D05"].total_cost == Decimal("3530.00")


def test_commission_rounds_half_up_to_the_cent() -> None:
    assert commission(Decimal("10560.00")) == Decimal("12.67")
    assert commission(Decimal("8337.50")) == Decimal("10.01")


def test_selling_everything_removes_the_position() -> None:
    portfolio = hand_example()
    portfolio.apply(make_trade(3, Side.SELL, 500, "37.00"))
    assert "D05" not in portfolio.positions


def test_selling_more_than_held_is_rejected_and_changes_nothing() -> None:
    portfolio = hand_example()
    with pytest.raises(OversellError, match="only 500 held"):
        portfolio.apply(make_trade(3, Side.SELL, 600, "37.00"))
    assert portfolio.positions["D05"].quantity == 500
    assert portfolio.realised_pnl == Decimal("0")


def test_selling_a_ticker_never_bought_is_rejected() -> None:
    with pytest.raises(OversellError, match="only 0 held"):
        Portfolio().apply(make_trade(1, Side.SELL, 100, "35.00"))


def test_back_dated_trade_is_rejected() -> None:
    portfolio = hand_example()
    with pytest.raises(OutOfOrderError, match="before the last trade"):
        portfolio.apply(make_trade(1, Side.BUY, 100, "35.00"))


def test_two_trades_on_the_same_day_are_allowed() -> None:
    portfolio = Portfolio()
    portfolio.apply(make_trade(1, Side.BUY, 100, "35.00"))
    portfolio.apply(make_trade(1, Side.BUY, 100, "36.00"))
    assert portfolio.positions["D05"].quantity == 200