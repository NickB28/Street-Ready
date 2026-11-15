"""Generate a seeded file of order commands for sgxbook.

Usage: python week-06/make_orders.py [count] [output_path]

Prices are integer cents, quantities are multiples of 100 (the board lot).
Every id is used once, and a CANCEL only names an order that was added earlier
and has not been cancelled yet (it may already have traded; the book decides).
"""

import random
import sys
from pathlib import Path

SEED = 2026
DEFAULT_COUNT = 100_000
DEFAULT_PATH = Path(__file__).parent / "data" / "orders_100k.csv"
MID_PRICE = 3750  # S$37.50
TICK = 10  # S$0.10 in cents


def generate(count: int, seed: int = SEED) -> list[str]:
    rng = random.Random(seed)
    lines: list[str] = []
    live_ids: list[int] = []
    next_id = 1
    while len(lines) < count:
        if live_ids and rng.random() < 0.2:
            pick = rng.randrange(len(live_ids))
            live_ids[pick], live_ids[-1] = live_ids[-1], live_ids[pick]
            lines.append(f"CANCEL,{live_ids.pop()}")
            continue
        side = rng.choice(["BUY", "SELL"])
        offset = rng.randint(-15, 15) * TICK
        price = MID_PRICE + offset
        qty = rng.randint(1, 10) * 100
        lines.append(f"ADD,{next_id},{side},{price},{qty}")
        live_ids.append(next_id)
        next_id += 1
    return lines


def main(argv: list[str]) -> int:
    count = int(argv[0]) if argv else DEFAULT_COUNT
    path = Path(argv[1]) if len(argv) > 1 else DEFAULT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(generate(count)) + "\n", encoding="utf-8")
    print(f"wrote {count} commands to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))