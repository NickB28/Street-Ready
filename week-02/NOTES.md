# Week 02 notes

## Environment

WSL2 with Ubuntu on Windows 11. I run the scripts and tests in the Ubuntu tab and use git only from Windows PowerShell. Tools: ShellCheck 0.11.0 and bats-core 1.13.0.

## What I built

- `make_fixture.sh` makes a throwaway messy folder of 44 files (dated names, undated names, spaces, uppercase extensions, no extension, hidden files, and a name collision).
- `tidy.sh` sorts files into `DEST/<category>/<YYYY-MM>/`, never overwrites, supports `--dry-run`, and logs every action.
- `backup.sh` makes a `.tar.gz` of the tidied folder, checks it can be read, logs its sha256 and keeps the newest 5.
- 13 bats tests that run the scripts like a user would. ShellCheck is clean on all three scripts.

## What I learnt

- `set -euo pipefail` makes a script stop on errors, unset variables and failed pipes. Under `set -e`, `((n++))` kills the script when n is 0, so I use `n=$((n + 1))`.
- Always quote variables (`"$file"`). File names with spaces break otherwise.
- `find -print0` with `read -r -d ''` is the safe way to loop over file names.
- `--dry-run` runs through the same code as the real run and only skips the move, so the preview matches what really happens.
- A backup is only done once it has been verified. A broken archive is deleted so it can't push a good one out of the newest 5.
- Two backups made in the same second would get the same name, so `backup.sh` waits until the name is free.
- A test is only trustworthy if it can fail. I broke a copy of each script on purpose (ignored `--dry-run`, kept 9 backups instead of 5) and watched the matching test go red.

## What broke and how I fixed it

- Running git from Ubuntu on `/mnt/c` showed every file as modified, because of line endings and permissions. Fix: git only from PowerShell, and `.gitattributes` forces LF for `*.sh` and `*.bats`.
- I ran `bash tidy.sh`, `shellcheck` and `bats` in the PowerShell tab ("No such file", "not recognized"). Fix: run them in the Ubuntu tab.
- Some pasted code pieces landed in the wrong place or were incomplete (a `return` inside an `if`, a loop before a variable was set). Fix: replace the whole file with the complete version.
- I added a duplicate `*.sh` line to `.gitattributes` by accident and removed it.
- I thought the collision file got a different name in the dry run and the real run. I had misread a screenshot, and a repeat check showed the order is the same.

## Resources

- Cletus's starting points: MIT Missing Semester (Shell Tools and Scripting), ShellCheck, bats-core docs, the `set -euo pipefail` search.
- `man find`, `man tar`, `man sort`, `man date`.

## LLM use (R6)

The scripts, tests and READMEs were written by Claude (an LLM) in small pieces during a chat. I pasted each piece, ran it, and committed only after it worked. I asked for a one or two line explanation of each part and I am going through every file line by line, so I can explain it myself. Prompts I used were like: "explain what the code does as we go along", "can you rewrite the whole code", and "what does this error mean".