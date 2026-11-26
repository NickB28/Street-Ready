# Week 07 NOTES: sshwatch

## How I made this (honest account)

## How I made this

**Resources I referred to:** I referred to my college OneNote materials and Claude (an AI assistant) for coding guidance, examples and debugging. I used AI-generated code for `parse.py`, `analyse.py`, `sshwatch.py` and the tests. I worked in VS Code, ran ruff, mypy and pytest, and completed the Git commits and pushes myself.

**What I wrote myself:** the five main regexes (log line, Failed password, Accepted password, Invalid user, Received disconnect). I built and tested them on regex101 (Python flavour) before implementing the code, as the brief required. They are in `my_regexes.txt`. I also referred to Claude when reviewing and improving the regexes. The username group in the Failed password regex was changed from `\S+` to `.+?` (see "What broke").

**Additional assistance:** I referred to Claude for the `message repeated N times` regex (`REPEAT_RE`), which was AI-generated. This is mentioned in a comment in `parse.py`.

I used Windows 11 PowerShell with a venv.

## What I learnt

- Syslog lines have no year, so the tool needs `--year`. When the month goes backwards (Dec to Jan) the year has to roll over.
- "message repeated N times" lines stand for several events, so one line can count as more than one failure.
- A sliding window with a deque is O(n), because each event is added once and removed once.
- Whether the window edge is inclusive or exclusive changes the results. I chose inclusive: failures exactly W minutes apart are inside the window.
- A golden file is only a snapshot of my own output. It catches changes, but it does not prove the output was right.

## What broke and how I fixed it

- **Cross-check mismatch (527 vs 528).** I counted Failed password lines independently with `Select-String` (520 lines plus the repeat lines, which add 8 more). The code found 527 and the count was 528. The cause was a real username with a leading space in the data (`invalid user  0101`). My original regex used `\S+` and missed it. Fix: changed the user group to `.+?` and regenerated the golden file.
- `invalid_user` was wrong for repeat lines because the code checked only the first 30 characters. Fix: `startswith`.
- ruff E501 (line length) and I001 (import order). Fix: `# ruff: noqa: E501` at the top of those files, and `ruff check . --fix`.
- mypy said a `type: ignore` was unused. I removed it.
- pytest "import file mismatch": `test_cli.py` clashed with week-04. Fix: the week-07 test files are named `test_sshwatch_*.py`.
- PowerShell `Out-File -Encoding utf8` adds a BOM, so the tests read the golden JSON with `utf-8-sig`.


## Known limits (honest)

- The disconnect regex `Received disconnect from (?P<ip>[^:]+):` does not handle IPv6 addresses, because IPv6 contains colons.
- I ran the full 655k-line log and the 100k and 300k cuts (see PERF in the README). Memory was flat at about 20 MB. The first full run took 21.1 s (cold file read), and later runs took 3.7 s.
- Commits only happened on Wed/Thu, so the rule of commits on three different days is not met for this week.
- Week 06 required fix: part (a) is done (NOTES corrected). For part (b), the hand-written HashMap, the code was written by Claude and not by me. The file says so in its header. I did not add a prompts list to the week-06 NOTES.


Most of my other messages were screenshots of my screen and short replies such as "done", "next" and "i am back". I do not have an exact copy of every message, so this list is not complete.

## Explain-it

**1. Main regex, group by group** (the log line regex I wrote):

`^(?P<month>\w+)\s+(?P<day>\d+)\s+(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})\s+(?P<host>\S+)\s+(?P<process>\w+)\[(?P<pid>\d+)\]:\s+(?P<message>.*)$`

- `^` and `$`: the match must cover the whole line.
- `month`: `\w+`, a word such as `Dec`.
- `day`: `\d+`, one or two digits (a single space or two spaces pad it).
- `hour`, `minute`, `second`: `\d{2}` each, with `:` between them.
- `host`: `\S+`, any run of non-space characters.
- `process`: `\w+`, for example `sshd`. The literal `\[` and `\]` match the brackets.
- `pid`: `\d+`, the process number.
- `message`: `.*`, everything after `: `. The other regexes search this part.

**2. Sliding window, line by line:** *not written yet.* I still need to go through `analyse.py` with Claude and write this in my own words.

**3. Three tests with the exact change that makes them fail:** *not done yet.* I still need to change the code by hand (for example the inclusive edge `>` in `analyse.py`) and record which test fails.