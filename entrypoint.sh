#!/bin/bash
set -e

DB_HOST="${HOST:-localhost}"
DB_PORT="${PORT:-5432}"
DB_USER="${USER:-odoo}"
DB_PASS="${PASSWORD:-}"
DB_NAME="${DB_NAME:-transitops}"

echo "=== TransitOps ==="
echo "DB: ${DB_NAME}@${DB_HOST}:${DB_PORT}"

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

DB_READY=$(python3 -c "
import psycopg2
try:
    c=psycopg2.connect(host='${DB_HOST}',port=${DB_PORT},user='${DB_USER}',password='${DB_PASS}',dbname='${DB_NAME}')
    cur=c.cursor()
    cur.execute(\"SELECT count(*) FROM information_schema.tables WHERE table_schema='public'\")
    print(cur.fetchone()[0])
    c.close()
except: print(0)
" 2>/dev/null)

echo "Tables: ${DB_READY}"

if [ "$DB_READY" -lt 10 ]; then
    echo "=== Initializing DB ==="
    odoo -d "${DB_NAME}" -i base --stop-after-init --no-http --db_host="${DB_HOST}" --db_port="${DB_PORT}" --db_user="${DB_USER}" --db_password="${DB_PASS}"
    echo "=== DB ready ==="
fi

echo "=== Starting Odoo ==="
exec "$@