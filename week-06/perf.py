"""Measure the order book and the binary search tree.

    python week-06/perf.py

Needs week-06/data/orders_100k.csv (make it with: python week-06/make_orders.py).
"""

import random
import time
from pathlib import Path

from book import OrderBook
from book_cli import replay
from ds.bst import TreeMap

ORDERS = Path(__file__).parent / "data" / "orders_100k.csv"
SEED = 2026
TREE_KEYS = 5000


def time_replay(runs: int = 3) -> tuple[float, int]:
    """Best-of-N seconds to replay the 100,000-command file, and the trade count."""
    best = float("inf")
    trades = 0
    for _ in range(runs):
        start = time.perf_counter()
        trades = len(replay(ORDERS, OrderBook()))
        best = min(best, time.perf_counter() - start)
    return best, trades


def measure_tree(prices: list[int]) -> tuple[int, float, float]:
    """Height after inserting the prices in order, insert seconds, lookup seconds."""
    tree: TreeMap[int, int] = TreeMap()
    start = time.perf_counter()
    for price in prices:
        tree.insert(price, price)
    insert_seconds = time.perf_counter() - start
    start = time.perf_counter()
    for price in prices:
        tree.get(price)
    lookup_seconds = time.perf_counter() - start
    return tree.height(), insert_seconds, lookup_seconds


def main() -> None:
    seconds, trades = time_replay()
    print(f"Replay of {ORDERS.name}: best of 3 = {seconds:.2f} s ({trades} trades)")
    random_prices = random.Random(SEED).sample(range(100_000), TREE_KEYS)
    for label, prices in (("random", random_prices), ("sorted", sorted(random_prices))):
        height, insert_s, lookup_s = measure_tree(prices)
        print(
            f"{TREE_KEYS} {label} prices: height {height}, "
            f"insert {insert_s:.3f} s, lookup all {lookup_s:.3f} s"
        )


if __name__ == "__main__":
    main()