#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL at ${HOST:-localhost}:${PORT:-5432}..."
until pg_isready -h "${HOST:-localhost}" -p "${PORT:-5432}" -U "${USER:-odoo}" -q 2>/dev/null; do
    echo "  PostgreSQL not ready yet, retrying in 3s..."
    sleep 3
done
echo "PostgreSQL is ready!"

# Generate odoo.conf from environment variables
cat > /etc/odoo/odoo.conf <<EOF
[options]
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
data_dir = /var/lib/odoo
db_host = ${HOST:-localhost}
db_port = ${PORT:-5432}
db_user = ${USER:-odoo}
db_password = ${PASSWORD:-}
admin_passwd = ${ODOO_ADMIN_PASSWD:-admin}
proxy_mode = True
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_time_cpu = 600
limit_time_real = 1200
limit_request = 8192
EOF

echo "Starting Odoo..."
exec "$@"
