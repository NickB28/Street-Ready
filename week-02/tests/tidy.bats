#!/usr/bin/env bats

setup() {
    TIDY="${TIDY:-$BATS_TEST_DIRNAME/../tidy.sh}"
    SRC="$BATS_TEST_TMPDIR/src"
    DEST="$BATS_TEST_TMPDIR/dest"
    mkdir -p "$SRC"
}

snapshot() {
    (cd "$1" && find . -type f -print0 | sort -z | xargs -0 sha256sum)
}

@test "--help exits 0 and shows usage" {
    run bash "$TIDY" --help
    [ "$status" -eq 0 ]
    [[ "$output" == *"Usage: tidy.sh"* ]]
}

@test "wrong number of arguments exits 1" {
    run bash "$TIDY" "$SRC"
    [ "$status" -eq 1 ]
}

@test "missing SOURCE exits 2" {
    run bash "$TIDY" "$BATS_TEST_TMPDIR/nope" "$DEST"
    [ "$status" -eq 2 ]
}

@test "--dry-run leaves SOURCE byte-for-byte unchanged" {
    printf 'one' > "$SRC/DBS_eStatement_2026-09.pdf"
    printf 'two' > "$SRC/OCBC 360 Sep 2026.pdf"
    printf 'three' > "$SRC/IMG_4021.JPG"
    printf 'hidden' > "$SRC/.DS_Store"
    before="$(snapshot "$SRC")"
    run bash "$TIDY" --dry-run "$SRC" "$DEST"
    [ "$status" -eq 0 ]
    after="$(snapshot "$SRC")"
    [ "$before" = "$after" ]
    [ ! -e "$DEST/statements" ]
}

@test "a filename with spaces lands in the right folder" {
    printf 'x' > "$SRC/OCBC 360 Sep 2026.pdf"
    touch -d '2026-09-15 12:00' "$SRC/OCBC 360 Sep 2026.pdf"
    run bash "$TIDY" "$SRC" "$DEST"
    [ "$status" -eq 0 ]
    [ -f "$DEST/statements/2026-09/OCBC 360 Sep 2026.pdf" ]
    [ ! -e "$SRC/OCBC 360 Sep 2026.pdf" ]
}

@test "a collision gets _1 and loses nothing" {
    mkdir -p "$SRC/old"
    printf 'first' > "$SRC/bank_statement_2026-09.pdf"
    printf 'second' > "$SRC/old/bank_statement_2026-09.pdf"
    run bash "$TIDY" "$SRC" "$DEST"
    [ "$status" -eq 0 ]
    [ "$(cat "$DEST/statements/2026-09/bank_statement_2026-09.pdf")" = "first" ]
    [ "$(cat "$DEST/statements/2026-09/bank_statement_2026-09_1.pdf")" = "second" ]
}

@test "running tidy twice is safe" {
    printf 'a' > "$SRC/receipt_ntuc_20260912.jpg"
    printf 'b' > "$SRC/budget_2026-05.xlsx"
    run bash "$TIDY" "$SRC" "$DEST"
    [ "$status" -eq 0 ]
    first="$(find "$DEST" -type f -not -path '*/logs/*' | wc -l)"
    run bash "$TIDY" "$SRC" "$DEST"
    [ "$status" -eq 0 ]
    [[ "$output" == *"moved=0 skipped=0 errors=0"* ]]
    second="$(find "$DEST" -type f -not -path '*/logs/*' | wc -l)"
    [ "$first" -eq 2 ]
    [ "$first" -eq "$second" ]
    [ -f "$DEST/images/2026-09/receipt_ntuc_20260912.jpg" ]
}

@test "the full fixture loses no files" {
    bash "$BATS_TEST_DIRNAME/../make_fixture.sh" "$SRC"
    total="$(find "$SRC" -type f | wc -l)"
    hidden="$(find "$SRC" -type f -name '.*' | wc -l)"
    run bash "$TIDY" "$SRC" "$DEST"
    [ "$status" -eq 0 ]
    moved="$(find "$DEST" -type f -not -path '*/logs/*' | wc -l)"
    [ "$moved" -eq $((total - hidden)) ]
}