# Week 03: sgdfx

A command-line tool that looks up and converts the MAS daily SGD per USD exchange rate. It uses only the Python standard library.

The data is "Exchange Rates, SGD per unit of USD, Daily" from MAS on data.gov.sg, saved in `data/sgd_usd_daily.csv`. It runs from January 1988 to October 2015, so the latest rate is from 19 October 2015.

## Run it

Windows PowerShell:

```powershell
git clone https://github.com/NickB28/Street-Ready.git
cd Street-Ready
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python week-03\sgdfx.py latest
pytest week-03
ruff check .
```

macOS / Linux:

```bash
git clone https://github.com/NickB28/Street-Ready.git
cd Street-Ready
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 week-03/sgdfx.py latest
pytest week-03
ruff check .
```

## Commands

The global `--file` option comes before the subcommand and reads a different CSV (`python week-03/sgdfx.py --file my.csv latest`).

### latest

```
$ python week-03/sgdfx.py latest
2015-10-19  1.3827 SGD per USD
```

### on DATE

If there is no rate that day (a weekend or a public holiday), the most recent earlier date is used and the tool says so.

```
$ python week-03/sgdfx.py on 2014-12-25
No rate for 2014-12-25 (weekend or holiday); using 2014-12-24.
2014-12-24  1.324 SGD per USD
```

### convert AMOUNT --from USD|SGD [--date DATE]

Uses the rate on that date (default: the latest) and rounds to 2 decimal places. It uses `Decimal`, not float.

```
$ python week-03/sgdfx.py convert 250 --from USD --date 2015-03-02
250 USD = 341.03 SGD  (rate 1.3641 on 2015-03-02)
```

### stats --start DATE --end DATE

```
$ python week-03/sgdfx.py stats --start 2015-01-01 --end 2015-01-31
Rates from 2015-01-01 to 2015-01-31
min   1.3246
max   1.3533
mean  1.3374
biggest move  0.0099 on 2015-01-20
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 1 | data problem: missing file, date before the data, empty range, negative amount |
| 2 | bad usage, such as a malformed date or an unknown option (from argparse) |

A data problem prints one line to stderr (`sgdfx: error: ...`) and never a traceback. Blank or malformed rows in the CSV are skipped, and the number skipped is reported on stderr.

## Tests

```bash
pytest week-03
```

There are 20 tests in `test_sgdfx.py`. They call `main(argv)` directly and use the small hand-written file `fixtures/rates_fixture.csv`, never the full download. The fixture has a weekend gap, a blank rate and a malformed rate.

CI runs `ruff check .` and `pytest` for the whole repo on every push and pull request (see `.github/workflows/ci.yml`).