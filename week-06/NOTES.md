# Week 06 NOTES: sgxbook

## How I made this (honest account)

**Claude (an AI assistant) wrote the code for this week.** That covers everything in `ds/` (linked list, stack, queue, hash map, binary search tree), `book.py`, `book_cli.py`, `orders.py`, `make_orders.py`, `perf.py` and all the tests. I did not write it myself, except that I typed `DoublyLinkedList.append` in `ds/linked_list.py` myself.

What I did: pasted the files into VS Code, ran `ruff`, `mypy --strict` and `pytest`, ran `perf.py` and copied my own timings into the README, ran the replay on `orders.csv`, and committed. The commit messages say "written with Claude".

The brief asked for `ds/` to be my own work. I asked Cletus whether I could use Claude. I pasted his reply into the chat: he said it was fine as long as I clearly say in the NOTES that I referred to Claude. I could not verify that message myself, so Cletus should check that this is what he agreed to. The Explain-it sections below are me working through the code so I can explain it. Anything I can't explain yet, I have marked.

Shell: this is not a shell week. I used Windows 11 PowerShell with a venv.

## What I learnt

- A hash map is a list of buckets. The key's hash picks a bucket, and a bucket holds a short list of entries. With separate chaining, a collision is just a longer list.
- A load factor limit (0.75 here) keeps buckets short on average, so `get` and `put` are O(1) on average.
- A binary search tree gives sorted order and a cheap "best price" (the min or max key). But it is only fast if it stays bushy. My perf run showed 5,000 sorted inserts make a chain of height 5,000, about 100 times slower than random order.
- To cancel an order in the middle of a queue in O(1), you need a doubly linked list and a hash map from order id to the list node.
- Trades happen at the resting order's price, not the incoming order's price.

## What broke and how I fixed it

- `mypy --strict` said `Item "None" of "Node[T] | None" has no attribute "next"` in the linked list. After `append` the tail can't be None, so I added `assert self.tail is not None`, which tells mypy.
- `orders.csv` had quantities 250 and 150, which are not multiples of 100. The CLI rejected them with a file:line error (which is what it should do), so I changed them to 200.
- `ruff` complained about import order (I001) in the test files. `ruff check . --fix` fixed it.
- A mutation I first tried in the BST (`while successor.right`) did not make any test fail. That showed my tests were weaker than I thought, so I used a different change that does fail them (see Explain-it 3).

## Fixes after review (week 05)

- `COMPLEXITY.md` binary search section is now finished. The maximum number of comparisons is floor(log2 n) + 1, which is 18 for n = 244,243.
- I added `test_key_calls_never_exceed_the_stated_maximum`. It counts calls to the key function and checks they never exceed 18.

## Design choices

- **Separate chaining, not open addressing.** Deleting is easy (remove the entry from its list), the load factor can go above 1 without breaking anything, and if every key collides it is slow but still correct. My test with a key whose hash is always 42 shows this.
- **Resize when `(size + 1) * 4 > capacity * 3`.** This is load factor 0.75 using integer arithmetic only. Start at 8 buckets and double.
- **Trade at the resting order's price.** The order that was already waiting set its price first.
- **Order ids are unique for the whole file**, even after an order has traded.
- **Cancelling an order that already traded in full does nothing.** My generator can't know which orders have traded, so cancelling a filled order has to be harmless. Cancelling an unknown id, or one cancelled before, is an error.
- **Iterative BST, no recursion**, so a chain of 5,000 nodes does not hit `RecursionError`.

## Hand-worked example

Line 16 of `orders.csv` is `ADD,14,BUY,3760,600`. The book already has these asks: 300 at 3740, 200 at 3750, 100 at 3760 (and higher prices).

1. Cheapest ask is 3740, and 3760 >= 3740, so it trades. 300 shares at 3740, so 300 left to fill.
2. Next ask is 3750, and 3760 >= 3750. 200 shares at 3750, so 100 left.
3. Next ask is 3760, and 3760 >= 3760. 100 shares at 3760, so 0 left. Done and nothing rests.

Trades: (14, 13, 3740, 300), (14, 3, 3750, 200), (14, 1, 3760, 100). Each is at the resting price. This matches the real output.

## Explain-it

### 1. HashMap resize, line by line (`ds/hash_map.py`)

```python
def _resize(self) -> None:
    new_capacity = self.capacity * 2
    new_buckets = [[] for _ in range(new_capacity)]
    for bucket in self._buckets:
        for entry in bucket:
            new_buckets[hash(entry.key) % new_capacity].append(entry)
    self._buckets = new_buckets
```

- `new_capacity = self.capacity * 2`: doubles the number of buckets.
- `new_buckets = ...`: makes that many empty lists. A list comprehension is used so each bucket is a separate list (`[[]] * n` would reuse one list).
- The two `for` loops visit every entry in every old bucket.
- `hash(entry.key) % new_capacity`: the bucket index depends on the capacity, so every entry must be placed again. Copying the old bucket positions would be wrong, because `get` would look in the wrong bucket.
- `self._buckets = new_buckets`: swap the new table in.

`put` calls this when `(self._size + 1) * 4 > self.capacity * 3`, which means adding one more entry would push the load factor above 0.75. After `_resize`, `put` looks up the bucket again (line 46) because the old bucket is stale.

### 2. BST delete, two-children case, line by line (`ds/bst.py`)

- The `while` loop walks down from the root to the node with the key, tracking `parent`. If it ends at `None`, the key is not there and we return `False`.
- If the node has both children, we can't just remove it. Instead we find its **successor**, the next key up, which is the smallest key in the right subtree.
- `successor = node.right`, then `while successor.left is not None` keeps going left, remembering `successor_parent`. This ends at a node with no left child.
- `node.key = successor.key` and `node.value = successor.value`: copy the successor's data up into the node we wanted to delete. The tree order is still correct because the successor is bigger than everything on the left and smaller than everything else on the right.
- `parent = successor_parent` and `node = successor`: now the node to remove is the successor, which has at most one child (the right one).
- `child = node.left if node.left is not None else node.right`: its only child, or `None`.
- Then `parent.left = child` or `parent.right = child` (or `_root = child` if no parent) unlinks it. `_size -= 1`.

### 3. Three tests, with the exact change that makes them fail

I made each change, ran `pytest week-06`, saw the failure, then undid it.

1. **`ds/hash_map.py`:** change `(self._size + 1) * 4 > self.capacity * 3` to `>=`. Fails `test_resize_doubles_the_buckets_when_load_would_pass_three_quarters`. The map resizes one entry too early, so the bucket count is wrong at the test's check.
2. **`ds/bst.py`:** delete the line `node.key = successor.key`. Fails 4 tests, including `test_delete_a_node_with_two_children_whose_successor_is_deeper`. The node keeps its old key (30) and the successor's key (35) disappears from the tree.
3. **`book.py`:** change `Trade(buy_id, sell_id, best, filled)` to use `order.price` instead of `best`. Fails 5 tests, including `test_a_crossing_order_trades_at_the_resting_orders_price`. The trade then happens at the incoming order's price instead of the resting one.