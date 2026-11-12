"""Benchmark the four sorts on real HDB resale prices and write BENCHMARKS.md."""

import argparse
import platform
import random
import sys
import time
from collections.abc import Callable
from pathlib import Path

from algos.sorts import heap_sort, insertion_sort, merge_sort, quick_sort
from hdb import DataError, load_sales

HERE = Path(__file__).parent
SEED = 2026
INSERTION_LIMIT = 16_000
WORST_CASE_SIZES = (2_000, 4_000, 8_000)

Sorter = Callable[[list[int]], list[int]]
Results = list[tuple[int, float]]


def naive_quick_sort(items: list[int]) -> list[int]:
    """Quicksort with the first element as pivot. Only here to show its worst case."""
    if len(items) <= 1:
        return list(items)
    pivot = items[0]
    smaller = [x for x in items[1:] if x < pivot]
    larger = [x for x in items[1:] if x >= pivot]
    return naive_quick_sort(smaller) + [pivot] + naive_quick_sort(larger)


def builtin_sorted(items: list[int]) -> list[int]:
    """The baseline: Python's built-in sorted()."""
    return sorted(items)


ALGORITHMS: list[tuple[str, Sorter, int | None]] = [
    ("insertion_sort", insertion_sort, INSERTION_LIMIT),
    ("merge_sort", merge_sort, None),
    ("quick_sort", quick_sort, None),
    ("heap_sort", heap_sort, None),
    ("sorted() baseline", builtin_sorted, None),
]


def best_time(sort: Sorter, data: list[int], runs: int) -> float:
    """Return the fastest of several timings, in seconds."""
    best = float("inf")
    for _ in range(runs):
        start = time.perf_counter()
        sort(data)
        best = min(best, time.perf_counter() - start)
    return best


def sizes_for(total: int) -> list[int]:
    """Return 1k, 2k, 4k ... doubling up to the data size, then the full size."""
    sizes: list[int] = []
    n = 1000
    while n <= total:
        sizes.append(n)
        n *= 2
    if sizes and sizes[-1] != total:
        sizes.append(total)
    return sizes


def measure(prices: list[int], runs: int) -> dict[str, Results]:
    """Time every algorithm at every size, printing progress as it goes."""
    results: dict[str, Results] = {}
    for name, sort, limit in ALGORITHMS:
        results[name] = []
        for n in sizes_for(len(prices)):
            if limit is not None and n > limit:
                break
            seconds = best_time(sort, prices[:n], runs)
            results[name].append((n, seconds))
            print(f"{name:<18} n={n:>8,}  {seconds:9.4f} s", flush=True)
    return results


def ratio_text(previous: tuple[int, float] | None, n: int, seconds: float) -> str:
    """Return t(2n)/t(n) if the previous size is exactly half, otherwise a dash."""
    if previous is None or previous[0] * 2 != n or previous[1] == 0:
        return "-"
    return f"{seconds / previous[1]:.2f}"


def table(results: Results) -> list[str]:
    """Format one algorithm's results as a markdown table."""
    lines = ["| n | seconds | doubling ratio t(2n)/t(n) |", "|---|---|---|"]
    previous: tuple[int, float] | None = None
    for n, seconds in results:
        lines.append(f"| {n:,} | {seconds:.4f} | {ratio_text(previous, n, seconds)} |")
        previous = (n, seconds)
    return lines


def worst_case(runs: int) -> list[str]:
    """Time the first-element-pivot quicksort on already-sorted input."""
    lines = [
        "| n | naive quicksort (s) | ratio | quick_sort (s) |",
        "|---|---|---|---|",
    ]
    previous: float | None = None
    for n in WORST_CASE_SIZES:
        data = list(range(n))
        naive = best_time(naive_quick_sort, data, runs)
        fast = best_time(quick_sort, data, runs)
        ratio = f"{naive / previous:.2f}" if previous else "-"
        lines.append(f"| {n:,} | {naive:.4f} | {ratio} | {fast:.4f} |")
        print(f"naive quicksort sorted n={n:>6,}  {naive:9.4f} s", flush=True)
        previous = naive
    return lines


def build_report(results: dict[str, Results], extra: list[str], info: str) -> str:
    """Assemble the BENCHMARKS.md text."""
    out = ["# Benchmarks", "", info, ""]
    for name, rows in results.items():
        out += [f"## {name}", "", *table(rows), ""]
    out += ["## Worst case live: first-element pivot on already-sorted input", "", *extra, ""]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    """Run the benchmark and write the report."""
    parser = argparse.ArgumentParser(description="Benchmark the sorts.")
    parser.add_argument("--data", type=Path, default=HERE / "data" / "resale_full.csv")
    parser.add_argument("--runs", type=int, default=5, help="timings per measurement")
    parser.add_argument("--output", type=Path, default=HERE / "BENCHMARKS.md")
    args = parser.parse_args(argv)
    try:
        sales, skipped = load_sales(args.data)
    except DataError as err:
        print(f"bench: error: {err}", file=sys.stderr)
        return 1
    prices = [sale.resale_price for sale in sales]
    if len(prices) < 1000:
        print("bench: error: need at least 1,000 valid rows", file=sys.stderr)
        return 1
    random.Random(SEED).shuffle(prices)
    sys.setrecursionlimit(50_000)
    info = (
        f"Python {platform.python_version()} on {platform.system()} {platform.machine()}. "
        f"Data: {len(prices):,} resale prices from {args.data.name} ({skipped} bad rows skipped), "
        f"shuffled with seed {SEED}. Each time is the best of {args.runs} runs "
        f"(time.perf_counter). Insertion sort stops at {INSERTION_LIMIT:,}."
    )
    results = measure(prices, args.runs)
    report = build_report(results, worst_case(args.runs), info)
    args.output.write_text(report, encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())