#!/usr/bin/env bash
set -euo pipefail
umask 077

: "${DATABASE_URL:?DATABASE_URL is required}"
: "${BACKUP_DIR:?BACKUP_DIR is required}"
: "${S3_ALIAS:?S3_ALIAS configured by mc is required}"
: "${S3_MARKDOWN_BUCKET:?S3_MARKDOWN_BUCKET is required}"

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
destination="${BACKUP_DIR}/${timestamp}"
mkdir -p "${destination}/markdown"
pg_dump --format=custom --no-owner --file="${destination}/database.dump" "${DATABASE_URL}"
mc mirror --overwrite "${S3_ALIAS}/${S3_MARKDOWN_BUCKET}" "${destination}/markdown"
sha256sum "${destination}/database.dump" > "${destination}/SHA256SUMS"
find "${destination}/markdown" -type f -print0 | sort -z | xargs -0 sha256sum >> "${destination}/SHA256SUMS"
echo "Backup completed: ${destination}"
