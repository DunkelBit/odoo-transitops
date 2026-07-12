#!/bin/sh
set -e

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-odoo}"
DB_PASS="${DB_PASS:-}"
DB_NAME="${DB_NAME:-transitops}"

echo "=== TransitOps Entry ==="
echo "Connecting to $DB_NAME at $DB_HOST:$DB_PORT"

# Init DB if empty
TABLES=$(PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'" 2>/dev/null || echo "0")
echo "Tables: $TABLES"

if [ "$TABLES" -lt 10 ]; then
    echo "=== Init DB ==="
    odoo --db_host="$DB_HOST" --db_port="$DB_PORT" --db_user="$DB_USER" --db_password="$DB_PASS" --db_name="$DB_NAME" -i base --stop-after-init --no-http
    echo "=== DB ready ==="
fi

echo "=== Starting Odoo ==="
exec odoo --db_host="$DB_HOST" --db_port="$DB_PORT" --db_user="$DB_USER" --db_password="$DB_PASS" --db_name="$DB_NAME"