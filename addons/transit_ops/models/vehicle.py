from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Vehicle(models.Model):
    _name = "transitops.vehicle"
    _description = "Vehicle"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="License Plate", required=True, tracking=True)
    model_name = fields.Char(string="Model", required=True, tracking=True)
    vehicle_type = fields.Selection(
        [
            ("truck", "Truck"),
            ("van", "Van"),
            ("trailer", "Trailer"),
        ],
        string="Type",
        required=True,
        default="truck",
        tracking=True,
    )
    status = fields.Selection(
        [
            ("available", "Available"),
            ("on_trip", "On Trip"),
            ("in_shop", "In Shop"),
            ("retired", "Retired"),
        ],
        string="Status",
        default="available",
        required=True,
        tracking=True,
    )
    max_load_capacity = fields.Float(string="Max Load Capacity (tonnes)", required=True)
    fuel_capacity = fields.Float(string="Fuel Capacity (litres)")
    current_odometer = fields.Float(string="Current Odometer (km)")
    acquisition_cost = fields.Monetary(
        string="Acquisition Cost",
        currency_field="currency_id",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )
    active = fields.Boolean(default=True)

    driver_ids = fields.Many2many(
        "transitops.driver",
        string="Assigned Drivers",
    )
    trip_ids = fields.One2many(
        "transitops.trip",
        "vehicle_id",
        string="Trips",
    )
    maintenance_ids = fields.One2many(
        "transitops.maintenance",
        "vehicle_id",
        string="Maintenance Records",
    )

    trip_count = fields.Integer(
        string="Trip Count",
        compute="_compute_trip_count",
    )
    total_maintenance_cost = fields.Monetary(
        string="Total Maintenance Cost",
        currency_field="currency_id",
        compute="_compute_costs",
        store=True,
    )
    total_fuel_cost = fields.Monetary(
        string="Total Fuel Cost",
        currency_field="currency_id",
        compute="_compute_costs",
        store=True,
    )
    total_revenue = fields.Monetary(
        string="Total Revenue",
        currency_field="currency_id",
        compute="_compute_costs",
        store=True,
    )
    roi = fields.Float(
        string="ROI (%)",
        compute="_compute_roi",
        store=True,
    )

    @api.depends("trip_ids")
    def _compute_trip_count(self):
        for rec in self:
            rec.trip_count = len(rec.trip_ids)

    @api.depends(
        "trip_ids.revenue",
        "trip_ids.fuel_consumed",
        "maintenance_ids.cost",
    )
    def _compute_costs(self):
        for rec in self:
            rec.total_revenue = sum(rec.trip_ids.mapped("revenue"))
            fuel_price_param = self.env["ir.config_parameter"].sudo().get_param(
                "transitops.fuel_price_per_litre", "1.50"
            )
            fuel_price = float(fuel_price_param)
            rec.total_fuel_cost = sum(rec.trip_ids.mapped("fuel_consumed")) * fuel_price
            rec.total_maintenance_cost = sum(rec.maintenance_ids.mapped("cost"))

    @api.depends("total_revenue", "total_maintenance_cost", "total_fuel_cost", "acquisition_cost")
    def _compute_roi(self):
        for rec in self:
            if rec.acquisition_cost:
                rec.roi = (
                    (rec.total_revenue - (rec.total_maintenance_cost + rec.total_fuel_cost))
                    / rec.acquisition_cost
                ) * 100
            else:
                rec.roi = 0.0

    def action_view_trips(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Trips",
            "res_model": "transitops.trip",
            "view_mode": "list,form,kanban",
            "domain": [("vehicle_id", "=", self.id)],
            "context": {"default_vehicle_id": self.id},
        }

    def action_view_maintenance(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Maintenance",
            "res_model": "transitops.maintenance",
            "view_mode": "list,form",
            "domain": [("vehicle_id", "=", self.id)],
            "context": {"default_vehicle_id": self.id},
        }
