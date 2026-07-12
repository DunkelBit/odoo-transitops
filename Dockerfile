FROM odoo:17

COPY addons/transit_ops /mnt/extra-addons/transit_ops
COPY entrypoint.sh /entrypoint.sh

RUN tr -d '\r' < /entrypoint.sh > /tmp/ep.sh && mv /tmp/ep.sh /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
