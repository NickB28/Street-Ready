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