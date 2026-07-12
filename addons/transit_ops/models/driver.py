from datetime import date, timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Driver(models.Model):
    _name = "transitops.driver"
    _description = "Driver"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Full Name", required=True, tracking=True)
    license_number = fields.Char("License Number", required=True, tracking=True)
    license_expiry = fields.Date("License Expiry", required=True, tracking=True)
    license_status = fields.Selection([
        ("valid", "Valid"),
        ("expiring_soon", "Expiring Soon"),
        ("expired", "Expired"),
    ], compute="_compute_license_status", store=True)
    phone = fields.Char("Phone")
    status = fields.Selection([
        ("available", "Available"),
        ("on_trip", "On Trip"),
        ("off_duty", "Off Duty"),
    ], default="available", required=True, tracking=True)
    active = fields.Boolean(default=True)

    trip_ids = fields.One2many("transitops.trip", "driver_id")
    vehicle_ids = fields.Many2many("transitops.vehicle", string="Assigned Vehicles")
    trip_count = fields.Integer(compute="_compute_trip_count")

    @api.depends("license_expiry")
    def _compute_license_status(self):
        today = date.today()
        for d in self:
            if not d.license_expiry:
                d.license_status = "valid"
            elif d.license_expiry < today:
                d.license_status = "expired"
            elif d.license_expiry <= today + timedelta(days=30):
                d.license_status = "expiring_soon"
            else:
                d.license_status = "valid"

    @api.depends("trip_ids")
    def _compute_trip_count(self):
        for d in self:
            d.trip_count = len(d.trip_ids)

    @api.constrains("license_number")
    def _check_unique_license(self):
        for d in self:
            if d.license_number:
                dup = self.search([
                    ("license_number", "=", d.license_number),
                    ("id", "!=", d.id)
                ])
                if dup:
                    raise ValidationError(
                        f"License '{d.license_number}' is already used by another driver."
                    )

    def action_view_trips(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Trips",
            "res_model": "transitops.trip",
            "view_mode": "list,form,kanban",
            "domain": [("driver_id", "=", self.id)],
            "context": {"default_driver_id": self.id},
        }

    # --- cron job entry point ---
    @api.model
    def _cron_check_license_expiry(self):
        today = date.today()
        soon = today + timedelta(days=30)

        expiring = self.search([("license_expiry", ">=", today), ("license_expiry", "<=", soon)])
        expired = self.search([("license_expiry", "<", today)])

        managers = self.env.ref("transitops.group_fleet_manager").users
        if not managers:
            return

        for drv in expiring:
            days_left = (drv.license_expiry - today).days
            self._send_alert(managers, drv, expired=False, days_left=days_left)

        for drv in expired:
            self._send_alert(managers, drv, expired=True)

    def _send_alert(self, managers, drv, expired=False, days_left=0):
        """Fire off an email to each fleet manager about a driver's license status."""
        if expired:
            subj = f"License Expired: {drv.name}"
            body = (
                f"<p><b>{drv.name}</b> (License: {drv.license_number}) "
                f"has an <b>expired</b> license — "
                f"expired on {drv.license_expiry.strftime('%B %d, %Y')}.</p>"
                f"<p>Don't assign this driver to any trips until renewed.</p>"
            )
        else:
            subj = f"License Expiring Soon: {drv.name}"
            body = (
                f"<p><b>{drv.name}</b> (License: {drv.license_number}) "
                f"expires in <b>{days_left} day(s)</b> "
                f"on {drv.license_expiry.strftime('%B %d, %Y')}.</p>"
                f"<p>Please get this renewed.</p>"
            )

        for m in managers:
            self.env["mail.mail"].create({
                "subject": subj,
                "body_html": body,
                "email_to": m.email,
                "auto_delete": True,
            }).send()
