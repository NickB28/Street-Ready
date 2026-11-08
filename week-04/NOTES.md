# Week 04 notes: lotbook

## Hand-worked example (D05)

Trades from `examples/trades.csv`, worked on paper first and then checked against the code.
Fee rule: 0.12% of trade value, minimum S$10.00, rounded half-up to the cent.

| # | Trade | Value | Commission | Effect |
|---|-------|-------|------------|--------|
| 1 | BUY 300 @ 35.20 | 10,560.00 | 0.12% = 12.672, rounds to **12.67** | cost = 10,560.00 + 12.67 = **10,572.67** |
| 2 | BUY 200 @ 36.10 | 7,220.00 | 0.12% = 8.664, under the minimum, so **10.00** | cost = 7,220.00 + 10.00 = **7,230.00** |
| | After both buys | 500 shares | | total cost = 10,572.67 + 7,230.00 = **17,802.67**, average cost = 17,802.67 / 500 = **35.60534** |
| 3 | SELL 400 @ 37.00 | 14,800.00 | 0.12% = 17.76 | proceeds = 14,800.00 - 17.76 = **14,782.24** |

Selling 400 of the 500 shares removes 400/500 of the cost:

- cost removed = 17,802.67 x 400 / 500 = **14,242.136**
- realised profit = 14,782.24 - 14,242.136 = **540.104**, which the report prints as 540.10
- the 100 shares left keep a cost of 17,802.67 - 14,242.136 = **3,560.534**

At the price in `prices.csv` (37.50) those 100 shares are worth 3,750.00, so the unrealised profit is 3,750.00 - 3,560.534 = **189.47**.

These are the same numbers the code produces: average cost 35.6053, realised 540.10 and unrealised 189.47 all appear in the report, and `tests/test_domain.py` asserts 35.60534, 540.104 and 3560.534.

## What I learnt

- Money must be `Decimal`, never `float`, because a float cannot store 0.1 exactly. `quantize(..., ROUND_HALF_UP)` rounds to the cent the way the fee rule says.
- A `frozen=True` dataclass cannot be changed after it is created, so a `Trade` that passed its checks in `__post_init__` stays valid for its whole life.
- Average cost: a sell removes the same fraction of the total cost as the fraction of shares sold. Realised profit is the sell proceeds minus that removed cost.
- One base exception (`LotbookError`) means the command line can catch a single type and still show a clear message for every rule that was broken.
- `main(argv)` returns an exit code instead of exiting, so the tests can call it directly and check the code and the output.
- `mypy --strict` forces a type hint on everything. With a mypy step in CI, a type error turns the build red.
- Git records when a commit was made, not when it was pushed. Spreading the work over several days means the commit times show several days.

## What broke and how I fixed it

- **ruff found 16 problems** (import order, lines over the length limit). I added `ruff.toml` with a line length of 100 and ran `ruff check . --fix`.
- **First CLI run crashed with a missing file**, because `prices.csv` did not exist yet. I created it, and the CLI now turns any unreadable file into a `cannot read ...` message with exit code 1.
- **`ruff` was "not recognized"** in a new PowerShell window, because the virtual environment was not active. Fix: run `.venv\Scripts\Activate.ps1` first.
- **Pasting several commands at once** into PowerShell sometimes left it stuck at the `>>` prompt. Fix: paste one line at a time.
- **A change that did not commit.** I ran `git add` before saving the file in VS Code, so nothing was staged and `git push` said "Everything up-to-date". Fix: save first (no dot on the tab), check that `git status` shows `modified:`, then add, commit and push.
- **Code pasted into the wrong window.** I pasted a Python line into PowerShell and got "The 'from' keyword is not supported". Code goes into the file in VS Code, and PowerShell is only for commands.
- **Deliberate red CI run:** I added `typo_demo.py` containing `x: int = "hello"`, and mypy turned the build red. Failed run: https://github.com/NickB28/Street-Ready/actions/runs/41894077267. I then deleted the file and the next run (#20) went green.

## Fixes after review

- **Week 03 `sgdfx`:** a date after the end of the data used to be called a weekend or holiday. It now exits 1 and says so, and `latest` warns on stderr if the newest rate is more than 7 days old. The message used to give the last date twice. It now reads `no rate for 2030-01-01: the data ends on 2015-10-19`.
- **`prices.csv` was trusted blindly.** A repeated ticker silently overwrote the earlier row, and a bad ticker gave a misleading message. Now a repeated ticker exits 1 and names both rows (`prices.csv row 4: duplicate ticker D05 (already on row 2)`). Every ticker is checked with the same `TICKER_PATTERN` that `Trade` uses, and a bad one exits 1 naming the file and row.
- **Ticker policy:** a ticker must already be valid exactly as written (2 to 4 capital letters or digits). Nothing is changed automatically, in the trades file or the prices file, so `d05` is rejected in both.
- **Tests:** 6 new tests through `main(argv)` (one duplicate, five invalid tickers), which makes 38 in week-04.

## How I used an LLM

I used Claude as an assistant while building this, working in small steps and checking each result myself. My prompts, paraphrased:

- "Here is my uncle's Week 04 brief. Give me one small step at a time, and explain each piece of code in one or two lines."
- "Rewrite the whole file" whenever a paste went wrong.
- I sent a screenshot after every step so the result could be checked.
- "Why did this fail?" for each error above.

Some of what I learnt also came from my college OneNote notes and other websites.

What I did myself: typed every command, ran every test, checked the program's output against my hand-worked D05 numbers, and made the commits and pushes. The Explain-it section below is where I show that I understand the code.

## Design decisions

**Why `Trade` is immutable.** A trade is a record of something that already happened, so it should never change. `Trade` is a frozen dataclass whose checks (ticker, board lot, price) run once in `__post_init__`. After that it can't be edited, so a bad value can't sneak in later and corrupt the ledger.

**Why exceptions rather than return codes.** A return code can be ignored, and a forgotten check silently lets bad data through. An exception stops the work until something deals with it, and it carries a message that says what was wrong. All the errors inherit from one `LotbookError`, so the CLI catches one type and turns it into a one-line message with exit code 1. The domain package never prints and never reads files. Only the CLI does input and output, which keeps the rules easy to test.

**Where the fee rule lives and why.** It lives in one place, `lotbook/fees.py` (`commission()` with `COMMISSION_RATE` and `MIN_COMMISSION`). `Portfolio` calls it for both buys and sells. The rule is made up for this task and could change, so there is exactly one place to edit and one place to test.

**Why trades must be in date order.** Average cost depends on the order of the trades, so a back-dated trade would change cost and profit that were already worked out. The portfolio rejects it with `OutOfOrderError`.

## Explain-it

### The CI workflow, line by line (`.github/workflows/ci.yml`)

- `name: CI`: the label shown in the Actions tab and the README badge.
- `on: push:` and `pull_request:`: run the workflow on every push and every pull request.
- `jobs:` / `test:`: one job, called `test`.
- `runs-on: ubuntu-latest`: GitHub starts a fresh Linux machine for the job.
- `steps:`: the steps run in order. If one fails, the job stops and the run goes red.
- `uses: actions/checkout@v4`: copies my repository onto that machine.
- `uses: actions/setup-python@v5`, `python-version: "3.12"`, `cache: pip`: installs Python 3.12 and keeps pip downloads for faster later runs.
- `name: Install pinned requirements` / `run: pip install -r requirements.txt`: installs the exact versions I pinned (pytest 9.1.1, ruff 0.17.3, mypy 2.4.1).
- `name: Lint with ruff` / `run: ruff check .`: checks the style of the whole repo. Any problem gives a non-zero exit code, so the run goes red.
- `name: Type-check with mypy` / `run: mypy --strict week-04`: checks the type hints in week-04. This is the step that went red on run #19 when I added `x: int = "hello"`.
- `name: Run tests` / `run: pytest`: runs every test in the repo, from week-01, week-03 and week-04.

### Three tests and the code change that would make each one fail

**1. `test_small_trade_pays_the_minimum_commission`** (`tests/test_domain.py`)
It buys a small trade where 0.12% comes to less than S$10 and checks that the commission is exactly S$10.00.
It would fail if, in `lotbook/fees.py`, I changed `MIN_COMMISSION = Decimal("10.00")` to `Decimal("5.00")`. A small trade would then be charged S$5.00 (or its own small percentage), not S$10.00.

**2. `test_commission_rounds_half_up_to_the_cent`** (`tests/test_domain.py`)
It uses a trade worth 8,337.50, where 0.12% is exactly 10.005, and checks that the commission is 10.01 (rounded half-up).
It would fail if, in `lotbook/fees.py`, I changed `ROUND_HALF_UP` to `ROUND_HALF_EVEN` (and the import). Half-even rounds 10.005 to the nearest even cent, which is 10.00, so the test would get 10.00 instead of 10.01.

**3. `test_partial_sell_books_the_hand_worked_profit`** (`tests/test_domain.py`)
It runs my hand-worked D05 example (buy 300, buy 200, sell 400) and checks that the realised profit is 540.104.
It would fail if, in `Portfolio._sell` in `lotbook/portfolio.py`, I changed `proceeds = value - commission` to `proceeds = value + commission`. A sell fee would then be added instead of deducted, giving proceeds of 14,817.76 and a profit of 575.624, not 540.104.