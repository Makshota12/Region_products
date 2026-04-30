#!/bin/sh

set -e

BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUTPUT_FILE="${BACKUP_DIR}/digital_product_maturity_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

echo "[db-backup] Creating backup: ${OUTPUT_FILE}"
PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
  -h "${DB_HOST:-db}" \
  -p "${DB_PORT:-5432}" \
  -U "${POSTGRES_USER:-postgres}" \
  -d "${POSTGRES_DB:-digital_product_maturity}" | gzip > "${OUTPUT_FILE}"

echo "[db-backup] Cleanup backups older than ${RETENTION_DAYS} days"
find "${BACKUP_DIR}" -type f -name "*.sql.gz" -mtime +"${RETENTION_DAYS}" -delete

echo "[db-backup] Backup finished successfully"
