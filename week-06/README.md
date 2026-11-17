# Week 06: sgxbook

A price-time-priority limit order book for one SGX stock, built on data structures written from scratch: a doubly linked list, a stack, a queue, a hash map and a binary search tree. Prices are integer cents (S$37.50 = 3750) and quantities are multiples of 100 (the board lot). There are no floats anywhere.

## Run it

Clone and set up (HTTPS, no SSH key needed):

```
git clone https://github.com/NickB28/Street-Ready.git
cd Street-Ready
```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python week-06\book_cli.py replay week-06\data\orders.csv
pytest week-06
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 week-06/book_cli.py replay week-06/data/orders.csv
pytest week-06
```

Exit codes: `0` ok, `1` data error (the message names the file and line), `2` usage error.

## Input format

One command per line:

```
ADD,<id>,<BUY|SELL>,<price_cents>,<qty>
CANCEL,<id>
```

An incoming order trades against the best opposite prices it can reach, oldest first within a price, at the **resting** order's price. Any unfilled part rests on the book.

Rules I chose where the brief was silent:

- Order ids are unique for the whole file, even after an order has traded.
- Cancelling an order that has already traded in full does nothing ("too late").
- Cancelling an id that was never added, or was already cancelled, is an error.

## Real output

`python week-06\book_cli.py replay week-06\data\orders.csv` (the 31-line hand-written file):

```
Trades (13):
  buy #12 sell #2 S$37.50 x 100
  buy #12 sell #3 S$37.50 x 100
  buy #6 sell #13 S$37.40 x 200
  buy #10 sell #13 S$37.40 x 100
  buy #14 sell #13 S$37.40 x 300
  buy #14 sell #3 S$37.50 x 200
  buy #14 sell #1 S$37.60 x 100
  buy #15 sell #1 S$37.60 x 100
  buy #17 sell #4 S$37.70 x 100
  buy #17 sell #5 S$37.80 x 100
  buy #23 sell #24 S$37.30 x 100
  buy #25 sell #24 S$37.30 x 100
  buy #9 sell #26 S$37.20 x 400
Best bid: S$37.10
Best ask: S$37.20
Top 5 bids:
  S$   37.10       200 shares
  S$   37.00       400 shares
Top 5 asks:
  S$   37.20       600 shares
  S$   37.60       100 shares
  S$   37.80       400 shares
  S$   37.90       300 shares
```

## How it fits together

| Piece | Used for |
|---|---|
| `TreeMap` (price to queue) | Best price, and levels in order, one tree per side |
| `Queue` (linked list) | Time priority inside one price |
| `HashMap` (id to queue node) | Finding an order to cancel without searching |
| `DoublyLinkedList.remove(node)` | Taking an order out of the middle of a queue in O(1) |

## PERF

Measured on my Windows 11 laptop with `python week-06\perf.py` (best of 3 for the replay). Times change a little from run to run.

- **Replay of 100,000 commands** (`make_orders.py`, seed 2026, 57,309 trades): **0.68 s** (limit in the brief: 10 s).
- **Tree height after 5,000 inserts:**

| Insert order | Height | Insert 5,000 | Look up all 5,000 |
|---|---|---|---|
| Random prices | 28 | 0.005 s | 0.003 s |
| Sorted prices | 5,000 | 0.579 s | 0.548 s |

**Why:** the tree does not rebalance. A random order spreads keys left and right, so the tree stays bushy and every step down halves the search roughly. Sorted keys always go to the right, so the tree becomes a chain that is as tall as it is long.

**What it does to Big-O:** `insert`, `get`, `delete`, `min_key` and `max_key` all cost O(height). Random: about O(log n) (here 28 steps for 5,000 keys). Sorted: O(n) each (5,000 steps), so building the tree takes O(n²) in total, which matches the roughly 100 times slower insert and 180 times slower lookup measured above. In-order iteration is O(n) either way. All methods are loops with no recursion, so the chain of 5,000 does not raise `RecursionError`.

**For the order book:** real prices move in steps, and a market that rises steadily would insert new price levels in ascending order. Making the tree self-balancing (an AVL tree or treap, stretch goal 1) would keep the height near log n. I did not do that this week.

## Layout

```
book_cli.py     command line (replay)
book.py         the order book
orders.py       shared types: Trade, BookError
make_orders.py  seeded 100,000-command generator (output is