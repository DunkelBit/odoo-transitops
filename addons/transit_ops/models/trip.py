from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Trip(models.Model):
    _name = "transitops.trip"
    _description = "Trip"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char("Trip Ref", required=True, readonly=True, default="New")
    vehicle_id = fields.Many2one("transitops.vehicle", "Vehicle", required=True, tracking=True)
    driver_id = fields.Many2one("transitops.driver", "Driver", required=True, tracking=True)

    origin = fields.Char("Origin", required=True)
    destination = fields.Char("Destination", required=True)
    departure_date = fields.Datetime("Departure")
    arrival_date = fields.Datetime("Arrival")

    status = fields.Selection([
        ("draft", "Draft"),
        ("dispatched", "Dispatched"),
        ("in_transit", "In Transit"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ], default="draft", required=True, tracking=True)

    cargo_description = fields.Text("Cargo")
    cargo_weight = fields.Float("Weight (tonnes)")
    fuel_consumed = fields.Float("Fuel (litres)")
    distance_km = fields.Float("Distance (km)")

    revenue = fields.Monetary("Revenue", currency_field="currency_id")
    currency_id = fields.Many2one("res.currency",
                                  default=lambda self: self.env.company.currency_id)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "transitops.trip") or "New"
        return super().create(vals_list)

    @api.constrains("cargo_weight")
    def _check_cargo_weight(self):
        for t in self:
            if t.cargo_weight and t.vehicle_id:
                cap = t.vehicle_id.max_load_capacity
                if t.cargo_weight > cap:
                    raise ValidationError(
                        f"Cargo is {t.cargo_weight}t but vehicle '{t.vehicle_id.name}' "
                        f"only handles {cap}t."
                    )

    @api.constrains("driver_id")
    def _check_driver_license(self):
        for t in self:
            if t.driver_id and t.driver_id.license_status == "expired":
                raise ValidationError(
                    f"Can't assign {t.driver_id.name} — their license is expired."
                )

    def action_dispatch(self):
        for t in self:
            if t.vehicle_id.status != "available":
                raise ValidationError(f"Vehicle '{t.vehicle_id.name}' isn't available right now.")
            if t.driver_id.status != "available":
                raise ValidationError(f"Driver '{t.driver_id.name}' isn't available right now.")

            t.status = "dispatched"
            t.vehicle_id.status = "on_trip"
            t.driver_id.status = "on_trip"

    def action_start(self):
        for t in self:
            t.status = "in_transit"

    def action_complete(self):
        for t in self:
            t.status = "completed"
            t.vehicle_id.status = "available"
            t.driver_id.status = "available"

    def action_cancel(self):
        for t in self:
            # release resources if they were assigned
            if t.status in ("dispatched", "in_transit"):
                t.vehicle_id.status = "available"
                t.driver_id.status = "available"
            t.status = "cancelled"

    def action_reset_to_draft(self):
        for t in self:
            if t.status != "cancelled":
                raise ValidationError("Only cancelled trips can go back to draft.")
            t.status = "draft"
