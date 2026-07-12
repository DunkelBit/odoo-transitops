#!/bin/bash
set -e

echo "Waiting for PostgreSQL at ${HOST:-localhost}:${PORT:-5432}..."
until pg_isready -h "${HOST}" -p "${PORT:-5432}" -U "${USER:-odoo}" -q 2>/dev/null; do
    echo "  waiting..."
    sleep 3
done
echo "PostgreSQL is ready!"

DB_NAME="${DB_NAME:-transitops}"

cat > /etc/odoo/odoo.conf <<EOF
[options]
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
data_dir = /var/lib/odoo
db_host = ${HOST}
db_port = ${PORT:-5432}
db_user = ${USER:-odoo}
db_password = ${PASSWORD:-}
db_name = ${DB_NAME}
admin_passwd = ${ODOO_ADMIN_PASSWD:-admin}
proxy_mode = True
list_db = False
EOF

echo "Config written. DB: ${DB_NAME}@${HOST}:${PORT}"

# Initialize DB schema if needed (fresh Render database has no tables)
HAS_TABLES=$(PGPASSWORD="${PASSWORD}" psql -h "${HOST}" -p "${PORT:-5432}" -U "${USER:-odoo}" -d "${DB_NAME}" -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'" 2>/dev/null || echo "0")
echo "Public tables found: ${HAS_TABLES}"

if [ "$HAS_TABLES" -lt 10 ]; then
    echo "Initializing database (first boot)..."
    odoo -d "${DB_NAME}" -i base --stop-after-init --no-http --db_host="${HOST}" --db_port="${PORT:-5432}" --db_user="${USER:-odoo}" --db_password="${PASSWORD}" 2>&1
    echo "Database ready!"
fi

echo "Starting Odoo..."
exec "$@"
