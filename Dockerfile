FROM odoo:17

EXPOSE 8069

COPY addons/transit_ops /mnt/extra-addons/transit_ops
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
