# Complexity analysis

All measured numbers come from `BENCHMARKS.md` (Python 3.14.7, Windows, 244,243 real HDB resale prices, best of 5 runs).

## Summary table

| Algorithm | Best | Average | Worst | Extra space | Stable? | In place? |
|---|---|---|---|---|---|---|
| insertion_sort | O(n) | O(n²) | O(n²) | O(1) | yes | yes |
| merge_sort | O(n log n) | O(n log n) | O(n log n) | O(n) | yes | no |
| quick_sort | O(n log n) | O(n log n) | O(n²) | O(log n) | no | yes |
| heap_sort | O(n log n) | O(n log n) | O(n log n) | O(1) | no | yes |
| binary search (lower_bound, upper_bound) | O(log n) | O(log n) | O(log n) | O(1) | not applicable | not applicable |

Notes on the table:

- **Insertion sort** is O(n) on already-sorted input because the inner loop never runs. It is stable because it shifts an item only while the item before it is strictly greater, so equal keys never pass each other.
- **Merge sort** is stable because on a tie the merge takes from the left half first. It needs O(n) extra space for the merged lists.
- **Quicksort** is not stable: the three-way partition swaps items across long distances. My version uses a median-of-three pivot and a three-way partition, so sorted, reversed and all-equal input stay fast, and a stack always handles the smaller part first so the stack holds at most about log2(n) ranges. The O(n²) worst case still exists in theory for a specially built input; it just does not occur on sorted, reversed or repeated data.
- **Heap sort** is not stable: building the heap and moving the maximum to the end reorders equal keys.
- **Binary search**: `lower_bound` and `upper_bound` always run until the search range is empty, so even their best case is O(log n). A plain "find x" could stop at once if the first middle item matched, giving O(1) best.
- The sorts in `algos/sorts.py` each return a **new** list and pair each item with its key first, so every one of them uses an extra O(n) for that copy. The table gives the space of the algorithm itself.

## Measured doubling ratios against theory

If time grows like n², doubling n should multiply the time by about **4**. For n log n it should be a little over **2** (about 2.1 to 2.2 at these sizes, because log n also grows).

| Algorithm | Measured ratios (1k up to 128k) | Theory | Verdict |
|---|---|---|---|
| insertion_sort | 3.78, 4.04, 4.18, 4.14 | 4 | matches |
| merge_sort | 2.26, 2.16, 2.14, 2.31, 2.29, 1.96, 2.42 | about 2.1 to 2.2 | matches |
| quick_sort | 2.07, 1.98, 2.08, 2.13, 2.01, 2.63, 2.81 | about 2.1 | matches to 32k, then higher |
| heap_sort | 2.29, 2.22, 2.21, 2.25, 2.35, 2.61, 2.31 | about 2.1 to 2.2 | slightly higher |
| sorted() | 3.55, 2.44, 2.15, 2.23, 2.20, 2.70, 2.71 | about 2.1 | matches apart from the first row |

Mismatches and likely causes:

- **Insertion sort at 1k to 2k (3.78):** below 4 because at small n the O(n) work (copying, loop set-up) is a noticeable share of the time. From 4k on it is 4.04 to 4.18, which is O(n²).
- **Quick sort at 64k and 128k (2.63 and 2.81):** higher than theory. My best explanation is CPU cache: above roughly 32k items the data no longer fits in the fast cache, and the partition step jumps around memory, so each extra doubling costs more than the operation count alone says. I did not measure cache misses, so this is a likely cause and not a proven one.
- **Heap sort (2.61 at 64k):** heap sort is known to have poor cache behaviour, because a parent and its children sit far apart in memory. That fits the extra slowdown, and the full-size row shows it too: 128,000 to 244,243 is a 1.9 times larger input, but the time grew 2.76 times (0.6119 to 1.6913), while merge and quick sort grew 2.0 times.
- **sorted() at 1k to 2k (3.55):** the times are 0.0000 s and 0.0001 s, which is at the limit of what the timer can resolve, so that ratio is noise.
- **The last row (244,243):** it is 1.91 times 128,000, not 2 times, so its ratio is shown as "-" in the tables. Merge sort grew 2.00 times (0.3944 to 0.7874) and quick sort 2.00 times (0.2409 to 0.4814), which is what n log n predicts for a 1.91 times larger input.

## The worst case live: quicksort with the first element as pivot

On already-sorted input the first element is always the smallest, so one side of every split is empty and the work is about n²/2.

| n | naive quicksort | ratio | my quick_sort |
|---|---|---|---|
| 2,000 | 0.1247 s | - | 0.0058 s |
| 4,000 | 0.4936 s | 3.96 | 0.0147 s |
| 8,000 | 1.9907 s | 4.03 | 0.0414 s |

The ratios are 3.96 and 4.03, which is the O(n²) signature. At 8,000 items the naive version takes 1.99 s, while my median-of-three, three-way version takes 0.04 s, about 48 times faster. The naive version also recurses to a depth of n, which is why it would hit `RecursionError` on 100,000 sorted items and why `quick_sort` uses a stack instead.

## Why insertion sort stops at 16,000

It takes 5.66 s at 16,000 and quadruples at every doubling. Extending that to the full 244,243 rows gives about 5.66 x (244,243 / 16,000)² = about 1,300 s, so roughly 22 minutes for a single run, and about 1.8 hours for the best-of-5 I use everywhere else. The trend is already clear by 16k.

## Why sorted() beats my merge sort

At the full 244,243 rows (best of 5):

| Sort | Seconds | Slower than sorted() by |
|---|---|---|
| sorted() | 0.0529 | 1 times |
| quick_sort | 0.4814 | about 9 times |
| merge_sort | 0.7874 | about 15 times |
| heap_sort | 1.6913 | about 32 times |

merge_sort and `sorted()` have the same Big-O (O(n log n)), so the gap is a constant factor, and a big one.

- **What it is written in:** `sorted()` and `list.sort()` call CPython's list sort, which is written in C. My sorts are Python, so every comparison, swap and loop step runs as interpreted bytecode, which is much slower than compiled C.
- **Type-specialised comparison:** when every item is the same simple type (here all `int`), CPython picks a fast comparison function once and skips the general "compare any two objects" machinery on every comparison. My code goes through the general `<=` each time, and also compares inside `(key, item)` tuples.
- **Timsort:** the algorithm behind `sorted()`. It first scans for **runs**, stretches of the input that are already ascending (or descending, which it reverses). Short runs are extended with a binary insertion sort to a minimum length, and then runs are merged in a way that keeps their sizes balanced, with a "galloping" mode when one run keeps winning. So already-sorted data takes only O(n), data that is a few sorted blocks costs very little, and the worst case is still O(n log n). It is stable and uses O(n) extra space.
- **What this test shows:** my data is a random shuffle, so there are almost no natural runs to exploit. Most of the 15 times gap here therefore comes from C versus Python and the specialised comparison, not from run detection. I measured the total gap, not each cause on its own, so that split is my reasoning and not a measurement.

## Binary search on 244,000 rows

- **Maximum comparisons:** each pass halves the range, so a search needs at most floor(log2(n)) + 1 passes. For n = 244,243: 2^17 =