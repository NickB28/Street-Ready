#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 TARGET_DIR" >&2
    exit 1
fi

target="$1"

if [ -e "$target" ] && [ -n "$(ls -A "$target")" ]; then
    echo "Refusing to use non-empty folder: $target" >&2
    exit 1
fi
mkdir -p "$target"

make_file() {
    # usage: make_file PATH [YYYY-MM-DD modified date]
    local path="$1"
    mkdir -p "$(dirname "$path")"
    printf 'fixture file: %s\n' "$path" > "$path"
    if [ "$#" -ge 2 ]; then
        touch -d "$2" "$path"
    fi
}

# Dated names
for month in 01 02 03 04 05 06 07 08 09; do
    make_file "$target/DBS_eStatement_2026-$month.pdf"
done
make_file "$target/receipt_ntuc_20260912.jpg"
make_file "$target/receipt_ntuc_20260905.jpg"
make_file "$target/receipt_fairprice_20260803.png"
make_file "$target/Grab receipt 20260915.jpg"
for n in 1 2 3 4 5 6; do
    make_file "$target/invoice_2026070$n.pdf"
done
for hour in 09 10 11; do
    make_file "$target/Screenshot 2026-09-10 at $hour.00.png"
done

# Undated names (the month must come from the modified date)
make_file "$target/IMG_4021.JPG" 2026-08-15
make_file "$target/IMG_4022.JPG" 2026-08-16
make_file "$target/IMG_4023.JPG" 2026-09-02
make_file "$target/IMG_4100.heic" 2026-07-20
make_file "$target/photo_beach.jpeg" 2026-06-11

# Spaces and uppercase extensions
make_file "$target/OCBC 360 Sep 2026.pdf" 2026-09-20
make_file "$target/UOB One statement.PDF" 2026-08-30

# Data and other files
make_file "$target/population_2025-12.csv"
make_file "$target/SGD_USD_daily.CSV" 2026-09-01
make_file "$target/budget_2026.xlsx" 2026-05-05
make_file "$target/config_backup.json" 2026-04-18
make_file "$target/sales_20260630.json"
make_file "$target/notes.txt" 2026-09-03
make_file "$target/archive.zip" 2026-03-09
make_file "$target/installer.exe" 2026-02-14
make_file "$target/todo.md" 2026-09-10

# No extension, and hidden files
make_file "$target/no_extension_file" 2026-09-04
make_file "$target/Makefile" 2026-09-05
make_file "$target/.hidden_settings"
make_file "$target/.DS_Store"

# Collision: same name, same month, same category
make_file "$target/bank_statement_2026-09.pdf"
make_file "$target/old/bank_statement_2026-09.pdf"

count="$(find "$target" -type f | wc -l)"
echo "Created $count files in $target"