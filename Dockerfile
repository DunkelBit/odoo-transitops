FROM odoo:17

USER root
COPY addons/transit_ops /mnt/extra-addons/transit_ops
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
USER odoo

ENTRYPOINT ["entrypoint.sh"]
