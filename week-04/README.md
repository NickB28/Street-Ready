# Week 04: lotbook

A typed ledger for an SGX share portfolio. You give it a CSV of trades and a CSV of current prices, and it prints what you hold, what it cost on average, what it is worth now, and the profit already banked.

## Rules it enforces

- Shares trade in board lots: the quantity must be a positive multiple of 100.
- Commission is 0.12% of the trade value, with a minimum of S$10.00, rounded half-up to the cent.
- Buy commission is added to the cost. Sell commission is deducted from the proceeds.
- Cost is tracked as an average cost per share.
- You cannot sell shares you do not hold, and trades must be in date order.

## Get the code

```
git clone https://github.com/NickB28/Street-Ready.git
cd Street-Ready
```

## Set up

Needs Python 3.12 or newer (CI runs 3.12, developed on 3.14).

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

## Run it

**Windows (PowerShell):**

```powershell
python week-04\lotbook_cli.py report week-04\examples\trades.csv --prices week-04\examples\prices.csv
```

**macOS / Linux:**

```bash
python3 week-04/lotbook_cli.py report week-04/examples/trades.csv --prices week-04/examples/prices.csv
```

Output:

```
TICKER       QTY    AVG COST      LAST         VALUE    UNREALISED
D05          100     35.6053      37.50       3750.00        189.47
O39          100     14.9000      15.20       1520.00         30.00
Z74          200      3.4000       3.30        660.00        -20.00
TOTAL                                         5930.00        199.47
Realised P&L: 540.10
```

## Input files

`trades.csv` has the columns `date,ticker,side,quantity,price`, where `side` is `BUY` or `SELL`.
`prices.csv` has the columns `ticker,price`, with one row for every ticker you still hold.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Report printed |
| 1 | Bad data or a missing file. The message names the file and row, for example `broken_trades.csv row 3` |
| 2 | Wrong command-line usage |

## Test and check

Run these from the repository root with the venv active:

```
pytest week-04
ruff check .
mypy --strict week-04
```

## Layout

- `lotbook/trade.py`: the immutable `Trade` and its validation
- `lotbook/fees.py`: the commission rule, in one place
- `lotbook/position.py`: shares held and average cost for one ticker
- `lotbook/portfolio.py`: applies trades in order and tracks realised profit
- `lotbook/errors.py`: the error types, all derived from `LotbookError`
- `lotbook_cli.py`: reads the CSVs and prints the report
- `tests/`: unit tests for the domain code and the command line
- `examples/`: sample trades, prices and a deliberately broken file