# Week 02: tidy.sh and backup.sh

Two bash scripts that tidy a messy Downloads folder and back up the result:

- `tidy.sh` moves files into `DEST/<category>/<YYYY-MM>/`, never overwrites, and logs every action.
- `backup.sh` makes a verified `.tar.gz` of the tidied folder and keeps the newest 5.
- `make_fixture.sh` builds a throwaway messy folder (44 files) so you never test on real files.

Tested on Ubuntu under WSL2 with ShellCheck 0.11.0 and bats-core 1.13.0.

## Get the code

Windows PowerShell:

```powershell
git clone https://github.com/NickB28/Street-Ready.git
cd Street-Ready\week-02
wsl
```

The scripts need Linux, so `wsl` opens Ubuntu in the same folder. Run every command below inside it.

macOS / Linux:

```bash
git clone https://github.com/NickB28/Street-Ready.git
cd Street-Ready/week-02
```

The scripts use GNU tools (`date -d`, `stat -c`, `sha256sum`, bash 4+). On Linux and WSL2 they work as they are. On macOS, install GNU coreutils and a newer bash first (`brew install coreutils bash`) and put them first on your PATH. I have not tested macOS.

## Install the tools

Ubuntu / WSL:

```bash
sudo apt update && sudo apt install -y shellcheck bats
```

macOS:

```bash
brew install shellcheck bats-core
```

Check the versions: `shellcheck --version` and `bats --version`.

## Try it safely

```bash
bash make_fixture.sh ~/messy
bash tidy.sh --dry-run ~/messy ~/tidied
bash tidy.sh ~/messy ~/tidied
bash backup.sh ~/tidied ~/backups
```

- `make_fixture.sh` refuses to use a folder that already has files in it.
- `--dry-run` writes log lines tagged `[DRY-RUN]` and moves nothing.
- Keep the backup folder outside DEST.
- To start over: `rm -rf ~/messy ~/tidied ~/backups`

## How tidy.sh sorts

| Extension (any case) | Category |
|---|---|
| pdf | statements |
| jpg, jpeg, png, heic | images |
| csv, xlsx, json | data |
| anything else | other |

The month comes from a date in the filename (`2026-09` or `20260912`), otherwise from the file's modified time. If the destination name is taken, the file becomes `name_1.ext`, `name_2.ext` and so on. Hidden files are skipped and logged as warnings.

## Exit codes

| Script | Code | Meaning |
|---|---|---|
| tidy.sh | 0 | success |
| tidy.sh | 1 | usage error |
| tidy.sh | 2 | SOURCE missing or unreadable |
| backup.sh | 0 | success |
| backup.sh | 1 | usage error |
| backup.sh | 2 | DEST missing or unreadable |
| backup.sh | 3 | could not create the archive |
| backup.sh | 4 | archive failed verification |

## Logs

- `DEST/logs/tidy-YYYYMMDD.log`: one line per action (timestamp, level, action, source, destination), ending with `moved=N skipped=N errors=N`.
- `BACKUP_DIR/backup.log`: archive created, verified with its sha256, and any old backups deleted.

## Tests and lint

```bash
bats tests/
shellcheck *.sh
```

`bats tests/` runs 13 tests that call the scripts the way a user would. `shellcheck` reports no warnings on any script.