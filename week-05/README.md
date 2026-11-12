# Week 05: hdbsort

Sorting and searching about 244,000 HDB resale flat transactions. Four sorting algorithms (insertion, merge, quick, heap) and binary search are written from scratch, with no `sorted()`, `list.sort()`, `heapq` or `bisect` inside `algos/`. A small command line uses them to answer questions about the data, and a benchmark measures how each sort scales.

## Get the code

```
git clone https://github.com/NickB28/Street-Ready.git
cd Street-Ready
```

## Set up

Needs Python 3.12 or newer.

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## The data

The repository includes `week-05/data/sample.csv`, a 5,000-row sample spread evenly over the full file (made by `make_sample.py`). The full file is about 23 MB, so it is not committed.

To get the full file: open the [HDB resale flat prices dataset on data.gov.sg](https://data.gov.sg/datasets/d_8b84c4ee58e3cfc0ece0d773c8ca6abc/view), click **Download CSV**, and save it as `week-05/data/resale_full.csv`. That path is git-ignored.

## Run it

Both commands work on the sample out of the box. Use `resale_full.csv` in the same place for the full dataset.

**Windows (PowerShell):**

```powershell
python week-05\hdb_cli.py range week-05\data\sample.csv --flat-type "4 ROOM" --min 500000 --max 600000
python week-05\hdb_cli.py top week-05\data\sample.csv --town TAMPINES -n 5
```

**macOS / Linux:**

```bash
python3 week-05/hdb_cli.py range week-05/data/sample.csv --flat-type "4 ROOM" --min 500000 --max 600000
python3 week-05/hdb_cli.py top week-05/data/sample.csv --town TAMPINES -n 5
```

Real output on the **full** dataset (about 244,000 rows):

```
hdb: skipped 69 bad rows in resale_full.csv
Flat type 4 ROOM, band S$500,000 to S$600,000
Sales in band: 27222
Median price: S$545,000
Cheapest: BUKIT BATOK S$500,000 (2017-01)
Dearest: YISHUN S$600,000 (2026-09)
```

```
hdb: skipped 69 bad rows in resale_full.csv
Top 5 sales in TAMPINES
 1. S$1,388,000  2026-09  MULTI-GENERATION 166.00 sqm
 2. S$1,275,000  2026-11  EXECUTIVE  142.00 sqm
 3. S$1,240,000  2026-06  EXECUTIVE  149.00 sqm
 4. S$1,210,000  2026-03  EXECUTIVE  147.00 sqm
 5. S$1,208,888  2026-10  EXECUTIVE  146.00 sqm
```

The `skipped` line goes to stderr: rows that cannot be read are counted and reported, never a crash.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Result printed |
| 1 | Data error: missing file, unknown flat type or town, `--min` above `--max` |
| 2 | Wrong command-line usage |

## Benchmark

```powershell
python week-05\bench.py
```

This times each sort on the real resale prices and writes `BENCHMARKS.md`. It takes a few minutes and needs the full file. See `COMPLEXITY.md` for what the numbers mean.

## Test and check

Run from the repository root with the virtual environment active:

```
pytest week-05
ruff check .
mypy --strict week-05
```

## Layout

- `algos/sorts.py`: insertion, merge, quick and heap sort
- `algos/search.py`: `lower_bound` and `upper_bound`
- `hdb.py`: the immutable `Sale` record and the CSV loader
- `hdb_cli.py`: the `range` and `top` commands
- `bench.py`: the benchmark
- `make_sample.py`: makes `data/sample.csv` from the full file
- `tests/`: unit tests for the loader, sorts, search and command line