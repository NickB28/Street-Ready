#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: tidy.sh [--dry-run] [-h|--help] SOURCE DEST

Move files from SOURCE into DEST/<category>/<YYYY-MM>/.
EOF
}

dry_run=0
positional=()

while [ "$#" -gt 0 ]; do
    case "$1" in
        -h|--help) usage; exit 0 ;;
        --dry-run) dry_run=1; shift ;;
        --) shift; positional+=("$@"); break ;;
        -*) echo "tidy.sh: unknown option: $1" >&2; usage >&2; exit 1 ;;
        *) positional+=("$1"); shift ;;
    esac
done

if [ "${#positional[@]}" -ne 2 ]; then
    usage >&2
    exit 1
fi

source_dir="${positional[0]}"
dest_dir="${positional[1]}"

if [ ! -d "$source_dir" ] || [ ! -r "$source_dir" ]; then
    echo "tidy.sh: SOURCE missing or unreadable: $source_dir" >&2
    exit 2
fi

# Temporary line so shellcheck sees every variable used. We remove it later.
echo "dry_run=$dry_run source=$source_dir dest=$dest_dir"