# Week 07: sshwatch

A command-line tool that reads an OpenSSH server log and reports on SSH brute-force attacks: which IPs hit hardest, which usernames bots try, and whether any login looks suspicious.

Data: the OpenSSH log from [Loghub](https://github.com/logpai/loghub) (logpai). Loghub is free to use for research and education, so see its repo for the licence terms. Thanks to the Loghub authors.

## Who wrote what

I used my colleges OneNote resources for coding guidance, alongside Claude for assistance with the parser, analysis, CLI and tests. I wrote the five main regexes myself using regex101 (Python flavour). The only exception was the message repeated N times regex, which Claude helped create. Further details are provided in NOTES.md.

## Get the code

Windows (PowerShell):

```powershell
git clone https://github.com/NickB28/Street-Ready.git
cd Street-Ready
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS / Linux:

```bash
git clone https://github.com/NickB28/Street-Ready.git
cd Street-Ready
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run it

The 2,000-line sample is included in `week-07/data/OpenSSH_2k.log`. The log has no year in it, so `--year` is required.

Windows:

```powershell
python week-07\sshwatch.py report week-07\data\OpenSSH_2k.log --year 2026 --top 5
```

macOS / Linux:

```bash
python3 week-07/sshwatch.py report week-07/data/OpenSSH_2k.log --year 2026 --top 5
```

Options: `--top N`, `--window MINUTES` (default 5), `--threshold FAILURES` (default 10), `--format text|json`.

## Get the full log (655,146 lines)

Download `SSH.tar.gz` from the Loghub OpenSSH page (https://github.com/logpai/loghub), extract it, and put `SSH.log` in `week-07/data/`. That path is git-ignored, so it is never committed.

## Real output

Part of the report for the 2k sample, run with `--top 5`. The full file is saved as `week-07/sample_report.txt`.

```
Top usernames tried (invalid users):
  admin     44
  oracle     6
  support    6
  test       5
  user       4

Successful logins:
  2026-12-10T09:32:20  fztu  119.137.62.142  (failures before: 0)

Brute force: >= 10 failures within 5 min (edge inclusive):
  183.62.140.253   first 2026-12-10T10:54:29  last 2026-12-10T11:04:43  peak 147
  187.141.143.180  first 2026-12-10T09:12:48  last 2026-12-10T09:20:02  peak 57
  103.99.0.122     first 2026-12-10T09:11:21  last 2026-12-10T11:04:45  peak 30
  112.95.230.3     first 2026-12-10T07:27:52  last 2026-12-10T07:28:51  peak 26
  5.188.10.180     first 2026-12-10T08:24:35  last 2026-12-10T08:26:24  peak 18
  185.190.58.151   first 2026-12-10T09:07:58  last 2026-12-10T09:12:59  peak 16
```

(The year 2026 is only what I passed to `--year`. The log does not contain a year.)

## FINDINGS

1. The hardest hitter was 183.62.140.253, with 147 failed logins inside one 5-minute window, between 10:54 and 11:04.
2. Six IPs crossed the brute-force threshold (10 or more failures within 5 minutes).
3. The bots mostly try `admin` (44 times), then `oracle`, `support`, `test` and `user`.
4. The only successful login is `fztu` from 119.137.62.142, with 0 failures before it. It does not look like a brute-force success.
5. Most failures happen between 07:00 and 11:00, and nothing happens overnight in this sample.

## PERF

Measured on Windows 11, Python in a venv, on the full Loghub OpenSSH log (655,146 lines, 73 MB), reading it as a stream. Time is wall-clock, and peak memory is the process's peak working set.

| File | Time | Peak memory |
|---|---|---|
| first 100,000 lines | 0.8 s | 18.8 MB |
| first 300,000 lines | 1.9 s | 20.1 MB |
| all 655k lines | 3.7 s | 20.8 MB |

Memory stays flat at about 20 MB, because only counters and a small window per IP are kept. The first full run I did took 21.1 s. That was the first read of the file, and my measuring script was polling the process. I did not repeat that cold-start run, so treat 3.7 s as the repeatable figure and 21 s as the worst case I saw. All 655,147 lines parsed with 0 unmatched.

I measured with a small PowerShell script written with Claude's help (it samples `PeakWorkingSet64` every 50 ms), which is not part of the repo.

## Tests and checks

```powershell
pytest
ruff check .
mypy --strict week-07
```

Window edge: failures exactly W minutes apart count as inside the window.