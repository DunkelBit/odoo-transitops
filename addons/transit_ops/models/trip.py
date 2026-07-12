from datetime import date

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Trip(models.Model):
    _name = "transitops.trip"
    _description = "Trip"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(string="Trip Reference", required=True, readonly=True, default="New")
    vehicle_id = fields.Many2one(
        "transitops.vehicle",
        string="Vehicle",
        required=True,
        tracking=True,
    )
    driver_id = fields.Many2one(
        "transitops.driver",
        string="Driver",
        required=True,
        tracking=True,
    )
    origin = fields.Char(string="Origin", required=True)
    destination = fields.Char(string="Destination", required=True)
    departure_date = fields.Datetime(string="Departure Date")
    arrival_date = fields.Datetime(string="Arrival Date")
    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("dispatched", "Dispatched"),
            ("in_transit", "In Transit"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
    )
    cargo_description = fields.Text(string="Cargo Description")
    cargo_weight = fields.Float(string="Cargo Weight (tonnes)")
    fuel_consumed = fields.Float(string="Fuel Consumed (litres)")
    distance_km = fields.Float(string="Distance (km)")
    revenue = fields.Monetary(
        string="Revenue",
        currency_field="currency_id",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("transitops.trip") or "New"
        return super().create(vals_list)

    @api.constrains("cargo_weight")
    def _check_cargo_weight(self):
        for rec in self:
            if rec.cargo_weight and rec.vehicle_id:
                if rec.cargo_weight > rec.vehicle_id.max_load_capacity:
                    raise ValidationError(
                        f"Cargo weight ({rec.cargo_weight}t) exceeds vehicle's "
                        f"maximum load capacity ({rec.vehicle_id.max_load_capacity}t)."
                    )

    @api.constrains("driver_id")
    def _check_driver_license(self):
        for rec in self:
            if rec.driver_id and rec.driver_id.license_status == "expired":
                raise ValidationError(
                    f"Driver '{rec.driver_id.name}' has an expired license. "
                    f"Cannot assign to trip."
                )

    def action_dispatch(self):
        for rec in self:
            if rec.vehicle_id.status != "available":
                raise ValidationError(
                    f"Vehicle '{rec.vehicle_id.name}' is not available for dispatch."
                )
            if rec.driver_id.status != "available":
                raise ValidationError(
                    f"Driver '{rec.driver_id.name}' is not available for dispatch."
                )
            rec.status = "dispatched"
            rec.vehicle_id.status = "on_trip"
            rec.driver_id.status = "on_trip"

    def action_start(self):
        for rec in self:
            rec.status = "in_transit"

    def action_complete(self):
        for rec in self:
            rec.status = "completed"
            rec.vehicle_id.status = "available"
            rec.driver_id.status = "available"

    def action_cancel(self):
        for rec in self:
            if rec.status in ("dispatched", "in_transit"):
                rec.vehicle_id.status = "available"
                rec.driver_id.status = "available"
            rec.status = "cancelled"

    def action_reset_to_draft(self):
        for rec in self:
            if rec.status != "cancelled":
                raise ValidationError("Only cancelled trips can be reset to draft.")
            rec.status = "draft"
