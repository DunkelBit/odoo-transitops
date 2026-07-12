#!/bin/bash
set -e

DB_HOST="${HOST:-localhost}"
DB_PORT="${PORT:-5432}"
DB_USER="${USER:-odoo}"
DB_PASS="${PASSWORD:-}"
DB_NAME="${DB_NAME:-transitops}"

echo "=== TransitOps Entry Point ==="
echo "DB: ${DB_NAME}@${DB_HOST}:${DB_PORT}"

# Generate odoo.conf
cat > /etc/odoo/odoo.conf <<CONF
[options]
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
data_dir = /var/lib/odoo
db_host = ${DB_HOST}
db_port = ${DB_PORT}
db_user = ${DB_USER}
db_password = ${DB_PASS}
db_name = ${DB_NAME}
admin_passwd = ${ODOO_ADMIN_PASSWD:-admin}
proxy_mode = True
list_db = False
CONF

echo "odoo.conf written."

# Check DB state using python (psql may not be available)
DB_READY=$(python3 -c "
import psycopg2, sys
try:
    conn = psycopg2.connect(host='${DB_HOST}', port=${DB_PORT}, user='${DB_USER}', password='${DB_PASS}', dbname='${DB_NAME}')
    cur = conn.cursor()
    cur.execute(\"SELECT count(*) FROM information_schema.tables WHERE table_schema='public'\")
    count = cur.fetchone()[0]
    print(count)
    conn.close()
except Exception as e:
    print('0')
" 2>/dev/null)

echo "Tables in DB: ${DB_READY}"

if [ "$DB_READY" -lt 10 ]; then
    echo "=== First boot — initializing Odoo base schema ==="
    odoo -d "${DB_NAME}" \
        -i base \
        --stop-after-init \
        --no-http \
        --db_host="${DB_HOST}" \
        --db_port="${DB_PORT}" \
        --db_user="${DB_USER}" \
        --db_password="${DB_PASS}" \
        --logfile=-
    echo "=== Database initialized ==="
fi

echo "=== Starting Odoo server ==="
exec "$@"
