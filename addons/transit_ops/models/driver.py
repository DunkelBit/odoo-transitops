from datetime import date, timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Driver(models.Model):
    _name = "transitops.driver"
    _description = "Driver"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Full Name", required=True, tracking=True)
    license_number = fields.Char(string="License Number", required=True, tracking=True)
    license_expiry = fields.Date(string="License Expiry", required=True, tracking=True)
    license_status = fields.Selection(
        [
            ("valid", "Valid"),
            ("expiring_soon", "Expiring Soon"),
            ("expired", "Expired"),
        ],
        string="License Status",
        compute="_compute_license_status",
        store=True,
    )
    phone = fields.Char(string="Phone")
    status = fields.Selection(
        [
            ("available", "Available"),
            ("on_trip", "On Trip"),
            ("off_duty", "Off Duty"),
        ],
        string="Status",
        default="available",
        required=True,
        tracking=True,
    )
    active = fields.Boolean(default=True)

    trip_ids = fields.One2many(
        "transitops.trip",
        "driver_id",
        string="Trips",
    )
    vehicle_ids = fields.Many2many(
        "transitops.vehicle",
        string="Assigned Vehicles",
    )

    trip_count = fields.Integer(
        string="Trip Count",
        compute="_compute_trip_count",
    )

    @api.depends("license_expiry")
    def _compute_license_status(self):
        today = date.today()
        for rec in self:
            if not rec.license_expiry:
                rec.license_status = "valid"
            elif rec.license_expiry < today:
                rec.license_status = "expired"
            elif rec.license_expiry <= today + timedelta(days=30):
                rec.license_status = "expiring_soon"
            else:
                rec.license_status = "valid"

    @api.depends("trip_ids")
    def _compute_trip_count(self):
        for rec in self:
            rec.trip_count = len(rec.trip_ids)

    @api.constrains("license_number")
    def _check_unique_license(self):
        for rec in self:
            if rec.license_number:
                existing = self.search(
                    [("license_number", "=", rec.license_number), ("id", "!=", rec.id)]
                )
                if existing:
                    raise ValidationError(
                        f"License number '{rec.license_number}' is already assigned to another driver."
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

    @api.model
    def _cron_check_license_expiry(self):
        today = date.today()
        threshold = today + timedelta(days=30)
        expiring = self.search([
            ("license_expiry", ">=", today),
            ("license_expiry", "<=", threshold),
        ])
        expired = self.search([
            ("license_expiry", "<", today),
        ])
        fleet_managers = self.env.ref("transitops.group_fleet_manager").users
        if not fleet_managers:
            return
        for driver in expiring:
            days_left = (driver.license_expiry - today).days
            subject = f"License Expiring Soon: {driver.name}"
            body = (
                f"<p>Driver <strong>{driver.name}</strong> "
                f"(License: {driver.license_number}) has a license expiring "
                f"in <strong>{days_left} day(s)</strong> "
                f"on <strong>{driver.license_expiry.strftime('%B %d, %Y')}</strong>.</p>"
                f"<p>Please arrange renewal before expiry.</p>"
            )
            for manager in fleet_managers:
                self.env["mail.mail"].create({
                    "subject": subject,
                    "body_html": body,
                    "email_to": manager.email,
                    "auto_delete": True,
                }).send()
        for driver in expired:
            subject = f"License Expired: {driver.name}"
            body = (
                f"<p>Driver <strong>{driver.name}</strong> "
                f"(License: {driver.license_number}) has an <strong>expired</strong> license "
                f"(expired on <strong>{driver.license_expiry.strftime('%B %d, %Y')}</strong>).</p>"
                f"<p>This driver should not be assigned to any trips until the license is renewed.</p>"
            )
            for manager in fleet_managers:
                self.env["mail.mail"].create({
                    "subject": subject,
                    "body_html": body,
                    "email_to": manager.email,
                    "auto_delete": True,
                }).send()
