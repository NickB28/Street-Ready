"""Price-time-priority limit order book for one stock.

Each side is a TreeMap from price to a Queue of resting orders (oldest first).
A HashMap from order id to the order's queue node makes CANCEL O(1) after lookup.
Prices are integer cents; quantities are shares in board lots of 100.
"""

from ds.bst import TreeMap
from ds.hash_map import HashMap
from ds.linked_list import Node
from ds.queue import Queue
from orders import BookError, Side, Trade


class _Order:
    def __init__(self, order_id: int, side: Side, price: int, qty: int) -> None:
        self.order_id = order_id
        self.side = side
        self.price = price
        self.qty = qty  # shares still unfilled


class OrderBook:
    def __init__(self) -> None:
        self._bids: TreeMap[int, Queue[_Order]] = TreeMap()
        self._asks: TreeMap[int, Queue[_Order]] = TreeMap()
        self._resting: HashMap[int, Node[_Order]] = HashMap()
        self._finished: HashMap[int, str] = HashMap()  # id -> "filled" or "cancelled"

    def _side_tree(self, side: Side) -> TreeMap[int, Queue[_Order]]:
        return self._bids if side == "BUY" else self._asks

    def add(self, order_id: int, side: Side, price: int, qty: int) -> list[Trade]:
        """Match against the other side first; rest any remainder on the book."""
        if order_id in self._resting or order_id in self._finished:
            raise BookError(f"duplicate order id {order_id}")
        order = _Order(order_id, side, price, qty)
        trades = self._match(order)
        if order.qty > 0:
            self._rest(order)
        else:
            self._finished.put(order_id, "filled")
        return trades

    def _match(self, order: _Order) -> list[Trade]:
        trades: list[Trade] = []
        buying = order.side == "BUY"
        other = self._asks if buying else self._bids
        while order.qty > 0 and len(other) > 0:
            best = other.min_key() if buying else other.max_key()
            if (buying and best > order.price) or (not buying and best < order.price):
                break
            level = other.get(best)
            assert level is not None
            resting = level.peek()
            filled = min(order.qty, resting.qty)
            order.qty -= filled
            resting.qty -= filled
            buy_id = order.order_id if buying else resting.order_id
            sell_id = resting.order_id if buying else order.order_id
            trades.append(Trade(buy_id, sell_id, best, filled))  # at the resting price
            if resting.qty == 0:
                level.dequeue()
                self._resting.delete(resting.order_id)
                self._finished.put(resting.order_id, "filled")
                if len(level) == 0:
                    other.delete(best)
        return trades

    def _rest(self, order: _Order) -> None:
        tree = self._side_tree(order.side)
        level = tree.get(order.price)
        if level is None:
            level = Queue()
            tree.insert(order.price, level)
        self._resting.put(order.order_id, level.enqueue(order))

    def cancel(self, order_id: int) -> None:
        node = self._resting.get(order_id)
        if node is None:
            state = self._finished.get(order_id)
            if state == "filled":
                return  # too late to cancel: it already traded in full
            if state == "cancelled":
                raise BookError(f"order {order_id} was already cancelled")
            raise BookError(f"unknown order id {order_id}")
        order = node.value
        tree = self._side_tree(order.side)
        level = tree.get(order.price)
        assert level is not None
        level.remove(node)
        if len(level) == 0:
            tree.delete(order.price)  # an empty level must not stay in the tree
        self._resting.delete(order_id)
        self._finished.put(order_id, "cancelled")

    def best_bid(self) -> int | None:
        return self._bids.max_key() if len(self._bids) > 0 else None

    def best_ask(self) -> int | None:
        return self._asks.min_key() if len(self._asks) > 0 else None

    def levels(self, side: Side, n: int) -> list[tuple[int, int]]:
        """Best-first (price, total quantity) for the top n levels of one side."""
        result: list[tuple[int, int]] = []
        for price, level in self._side_tree(side).items(descending=side == "BUY"):
            if len(result) == n:
                break
            result.append((price, sum(order.qty for order in level)))
        return result