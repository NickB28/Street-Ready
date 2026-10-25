#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: backup.sh [-h|--help] DEST BACKUP_DIR

Archive DEST into BACKUP_DIR/tidy-backup-YYYYMMDD-HHMMSS.tar.gz,
verify it, log its sha256 and keep only the newest 5 backups.
EOF
}

log() {
    printf '%s %s %s %s\n' "$(date -Iseconds)" "$1" "$2" "$3" >> "$log_file"
}

case "${1:-}" in
    -h|--help) usage; exit 0 ;;
esac

if [ "$#" -ne 2 ]; then
    usage >&2
    exit 1
fi

dest_dir="$1"
backup_dir="$2"
keep=5

if [ ! -d "$dest_dir" ] || [ ! -r "$dest_dir" ]; then
    echo "backup.sh: DEST missing or unreadable: $dest_dir" >&2
    exit 2
fi

mkdir -p "$backup_dir"
log_file="$backup_dir/backup.log"

archive="$backup_dir/tidy-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
while [ -e "$archive" ]; do
    sleep 1
    archive="$backup_dir/tidy-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
done

if ! tar -czf "$archive" -C "$dest_dir" .; then
    echo "backup.sh: could not create archive: $archive" >&2
    log ERROR create "archive=\"$archive\""
    exit 3
fi
log INFO create "archive=\"$archive\""

if ! tar -tzf "$archive" > /dev/null; then
    echo "backup.sh: verification failed: $archive" >&2
    log ERROR verify "archive=\"$archive\" removed=yes"
    rm -f -- "$archive"
    exit 4
fi

hash="$(sha256sum "$archive" | cut -d ' ' -f 1)"
log INFO verify "archive=\"$archive\" sha256=$hash"
echo "created: $archive"
echo "sha256: $hash"

mapfile -d '' -t backups < <(find "$backup_dir" -maxdepth 1 -type f -name 'tidy-backup-*.tar.gz' -print0 | sort -z)
excess=$((${#backups[@]} - keep))
if [ "$excess" -gt 0 ]; then
    for old in "${backups[@]:0:excess}"; do
        rm -- "$old"
        log INFO delete "archive=\"$old\""
        echo "deleted: $old"
    done
fi