#!/usr/bin/env bash
set -euo pipefail

: "${DATABASE_URL:?DATABASE_URL is required}"
: "${RESTORE_DIR:?RESTORE_DIR is required}"
: "${S3_ALIAS:?S3_ALIAS configured by mc is required}"
: "${S3_MARKDOWN_BUCKET:?S3_MARKDOWN_BUCKET is required}"
[[ "${CONFIRM_RESTORE:-}" == "RESTORE" ]] || { echo "Set CONFIRM_RESTORE=RESTORE" >&2; exit 2; }

(cd "${RESTORE_DIR}" && sha256sum --check SHA256SUMS)
pg_restore --clean --if-exists --no-owner --dbname="${DATABASE_URL}" "${RESTORE_DIR}/database.dump"
mc mirror --overwrite --remove "${RESTORE_DIR}/markdown" "${S3_ALIAS}/${S3_MARKDOWN_BUCKET}"
echo "Restore completed from: ${RESTORE_DIR}"
