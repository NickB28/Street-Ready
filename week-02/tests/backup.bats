#!/usr/bin/env bats

setup() {
    BACKUP="${BACKUP:-$BATS_TEST_DIRNAME/../backup.sh}"
    DEST="$BATS_TEST_TMPDIR/dest"
    OUT="$BATS_TEST_TMPDIR/backups"
    mkdir -p "$DEST"
    printf 'one' > "$DEST/a.txt"
    printf 'two' > "$DEST/b.txt"
}

@test "--help exits 0 and shows usage" {
    run bash "$BACKUP" --help
    [ "$status" -eq 0 ]
    [[ "$output" == *"Usage: backup.sh"* ]]
}

@test "missing DEST exits 2" {
    run bash "$BACKUP" "$BATS_TEST_TMPDIR/nope" "$OUT"
    [ "$status" -eq 2 ]
}

@test "creates a readable archive and logs its sha256" {
    run bash "$BACKUP" "$DEST" "$OUT"
    [ "$status" -eq 0 ]
    archive="$(ls "$OUT"/tidy-backup-*.tar.gz)"
    tar -tzf "$archive" > /dev/null
    hash="$(sha256sum "$archive" | cut -d ' ' -f 1)"
    grep -q "sha256=$hash" "$OUT/backup.log"
}

@test "rotation leaves exactly 5 archives after 7 runs" {
    for i in 1 2 3 4 5 6 7; do
        run bash "$BACKUP" "$DEST" "$OUT"
        [ "$status" -eq 0 ]
    done
    count="$(find "$OUT" -name 'tidy-backup-*.tar.gz' | wc -l)"
    [ "$count" -eq 5 ]
    [ "$(grep -c ' delete ' "$OUT/backup.log")" -eq 2 ]
}

@test "a broken archive makes backup exit 4 and is removed" {
    mkdir -p "$BATS_TEST_TMPDIR/fakebin"
    printf '%s\n' '#!/usr/bin/env bash' \
        'if [ "$1" = "-czf" ]; then echo garbage > "$2"; exit 0; fi' \
        'exec /usr/bin/tar "$@"' > "$BATS_TEST_TMPDIR/fakebin/tar"
    chmod +x "$BATS_TEST_TMPDIR/fakebin/tar"
    PATH="$BATS_TEST_TMPDIR/fakebin:$PATH" run bash "$BACKUP" "$DEST" "$OUT"
    [ "$status" -eq 4 ]
    [ "$(find "$OUT" -name 'tidy-backup-*.tar.gz' | wc -l)" -eq 0 ]
    grep -q ' ERROR verify ' "$OUT/backup.log"
}