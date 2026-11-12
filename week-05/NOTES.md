# Week 05 notes: hdbsort

## What I learnt
- Sorting is about trade-offs. Insertion sort is simple but O(n²), so it is only run up to 16,000 rows in the benchmark. Merge and heap sort are O(n log n) in every case. Quick sort is O(n log n) on average, and its worst case depends on the pivot.
- Binary search needs a loop invariant. If I can say what is true of everything left of `lo` and right of `hi`, the code almost writes itself.
- `lower_bound` and `upper_bound` differ by one comparison (`<` vs `<=`). That one character decides whether duplicates are included or excluded.
- A benchmark means more than one run. I took the best of 5 and looked at the ratio when n doubles. About 2x means n log n, about 4x means n².

## What broke and how I fixed it
- CI runs #32 to #35 went red. `ruff` found a 104-character line in `tests/test_loader.py` (E501, limit 100). Ruff runs first, so the job stopped in about 11 seconds. I wrapped the f-string in brackets (commit 53af0fd) and CI #36 went green. Lesson: run `ruff check .` and read "All checks passed!" before committing.
- I saved `bench.py` into `C:\Windows\System32` because PowerShell had opened there. I changed into the repo, activated the venv, and saved the file again in the right place.
- Several times I pasted code without saving the file (white dot on the tab), so git said "nothing to commit". Now I save and check that `git status` shows the file as modified before `git add`.
- The full dataset has 69 rows that cannot be parsed. The loader counts them and prints "skipped N bad rows" instead of crashing.

## Fixes after review (last week's required fix)
- `lotbook` prices.csv now rejects a duplicate ticker (the error names both rows) and an invalid ticker (it reuses `TICKER_PATTERN` from the trade code, so there is one rule).
- `sgdfx` now says "no rate for {day}: the data ends on {last_day}".

## How I used an LLM
Claude wrote most of the code in this week's folder, and I did not write it alone. I asked in small steps, pasted the code into VS Code, ran it, and fixed the problems I hit (above). I also used my college OneNote notes for the basics of sorting and Big-O. I changed the three lines in the Explain-it section below myself, to check I understood them.

## Design decisions
- **Floor area is a `Decimal`**, not a `float`. Values like 67.5 are stored exactly, so there is no 0.1 + 0.2 style rounding.
- **Price is an `int`** in whole dollars. The loader rejects anything that is not a whole number or is outside 0 to 1 billion.
- **Quick sort uses a median-of-three pivot and a 3-way partition.** A plain first-element pivot is O(n²) on already-sorted data, which is common. The 3-way partition makes lots of equal keys cheap.
- **Quick sort is iterative with an explicit stack and pushes the larger part first.** The next part to be handled is always the smaller one, so the stack stays at about log2(n) deep. There is no `RecursionError` on 100,000 sorted items (there is a test for this).
- **Stability:** insertion sort and merge sort are stable (equal keys keep their order). Quick sort and heap sort are not, because they swap items across long distances, which can jump an equal item over another one.

## Explain-it

### 1. The merge step (`_merge`), line by line
- `merged = []; i = j = 0`: an empty result and a position in each sorted list.
- `while i < len(left) and j < len(right)`: keep going while both lists still have items.
- `if left[i][0] <= right[j][0]`: compare the two front keys (`[0]` is the key, `[1]` is the item).
- If the left one is smaller or equal, append it and move `i` on. Otherwise append the right one and move `j` on.
- `<=` (not `<`) means that on a tie the left item goes first. Left items came earlier in the original list, so equal keys keep their order. That is what makes it stable.
- `merged.extend(left[i:])` and `merged.extend(right[j:])`: one list ran out, and whatever is left in the other is already sorted, so it is copied on the end.

### 2. `lower_bound`: invariant and why it stops
- Invariant: everything at an index below `lo` has key `< x`, and everything at index `hi` or above has key `>= x`. So the answer is always between `lo` and `hi`.
- `mid` is the middle. If its key is `< x`, then it and everything left of it are too small, so `lo = mid + 1`. Otherwise `mid` could be the answer, so `hi = mid`.
- Termination: `lo < hi` while looping, so `mid` is at least `lo` and less than `hi`. Either `lo` goes up to `mid + 1` or `hi` drops to `mid`, so `hi - lo` shrinks every pass. It reaches 0, the loop ends, and `lo == hi` is the answer.
- `upper_bound` is the same with `<=`, so it finds the first key `> x`.

### 3. Three tests, and the change that makes each fail
1. **`test_equal_keys_keep_their_original_order[merge_sort]`.** In `_merge`, change `<=` to `<`. Equal keys then take from the right first, so the order is no longer stable and the test fails.
2. **`test_repeated_value_spans_its_whole_run`.** In `upper_bound`, change `if value <= x:` to `if value < x:`. For `[1, 3, 3, 3, 5, 8, 8, 13]` and x = 3, `upper_bound` returns 1 instead of 4. The pair is `(1, 1)` instead of `(1, 4)`, so the test fails.
3. **`test_top_lists_the_dearest_sales_first`.** In `cmd_top`, change `ranked[::-1][: args.n]` to `ranked[: args.n]`. The list is sorted cheapest first, so without the reverse `top` shows the cheapest sales, and the test fails.