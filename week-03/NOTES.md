# Week 03 notes

## What I built

`sgdfx.py` is a command-line tool over the MAS daily SGD per USD rates. It has four subcommands (`latest`, `on`, `convert`, `stats`) and a global `--file` option. There are 20 pytest tests, and GitHub Actions runs ruff and pytest on every push.

## What I learnt

- `argparse` subcommands: each one has its own arguments, and bad usage exits with code 2 automatically.
- Making `main(argv)` return an exit code instead of exiting lets tests call it directly and check the output with `capsys`.
- `Decimal` is exact for money. `float` can give tiny errors such as 0.1 + 0.2.
- `bisect_right` finds the last row on or before a date. That is how a weekend or holiday falls back to the earlier day.
- The real data is weekly in the early years and daily later, so the "use the earlier date" rule matters.
- A CI workflow is a YAML file: when to run, which machine, and which steps. If a step fails, the run goes red.
- YAML depends on indentation, so I paste it into the editor rather than the terminal.

## What broke and how I fixed it

- The first `ruff check .` found 16 problems. I set `ruff.toml` to the rules I understand (E, F, I) with a line limit of 100, then `ruff check . --fix` sorted the imports.
- I pasted a `ruff.toml` into PowerShell instead of a file. It did nothing, so I created the file properly.
- The CI YAML came out with broken indentation when written from the terminal. I rewrote it in VS Code.
- I opened `.pytest_cache/README.md` instead of the real README by mistake. I added the CI badge from PowerShell instead.

## CI proof

- Green run on `main`: the workflow in `.github/workflows/ci.yml` passed (commit `4cad2cb`).
- Deliberately red run: https://github.com/NickB28/Street-Ready/actions/runs/40749609591
- On the branch `break-a-test` I changed one assertion so a test would fail, pushed it, and CI went red. I then reverted the commit and the branch went green again. `main` was never broken.

## Resources

- Python docs: argparse tutorial, `decimal`, `bisect`.
- GitHub docs: building and testing Python with Actions.
- Ruff documentation.
- The MAS dataset on data.gov.sg.

## LLM use (R6)

Claude wrote `sgdfx.py`, the tests, the workflow file and the READMEs in small pieces during a chat. I pasted each piece, ran it, compared the output to what was expected, and committed once it worked. I broke a test and the code on purpose to see the tests and CI fail. I am going through every file line by line so I can explain it.

## Next steps

- Try the stretch goals: a Windows CI matrix and a --format json option.
- Explain every line of the workflow file and every test out loud before submitting (R6).
