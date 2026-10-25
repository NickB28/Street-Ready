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
echo "created: $archive"