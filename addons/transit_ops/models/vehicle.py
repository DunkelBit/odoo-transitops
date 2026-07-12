from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Vehicle(models.Model):
    _name = "transitops.vehicle"
    _description = "Vehicle"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("License Plate", required=True, tracking=True)
    model_name = fields.Char("Model", required=True, tracking=True)
    vehicle_type = fields.Selection([
        ("truck", "Truck"),
        ("van", "Van"),
        ("trailer", "Trailer"),
    ], string="Type", default="truck", required=True, tracking=True)
    status = fields.Selection([
        ("available", "Available"),
        ("on_trip", "On Trip"),
        ("in_shop", "In Shop"),
        ("retired", "Retired"),
    ], string="Status", default="available", required=True, tracking=True)

    max_load_capacity = fields.Float("Max Load (tonnes)", required=True)
    fuel_capacity = fields.Float("Fuel Capacity (litres)")
    current_odometer = fields.Float("Odometer (km)")
    acquisition_cost = fields.Monetary("Acquisition Cost", currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
    active = fields.Boolean(default=True)

    # relations
    driver_ids = fields.Many2many("transitops.driver", string="Assigned Drivers")
    trip_ids = fields.One2many("transitops.trip", "vehicle_id", string="Trips")
    maintenance_ids = fields.One2many("transitops.maintenance", "vehicle_id")

    # computed
    trip_count = fields.Integer(compute="_compute_trip_count", string="Trips")
    total_maintenance_cost = fields.Monetary("Maintenance Cost", currency_field="currency_id",
                                             compute="_compute_costs", store=True)
    total_fuel_cost = fields.Monetary("Fuel Cost", currency_field="currency_id",
                                      compute="_compute_costs", store=True)
    total_revenue = fields.Monetary("Revenue", currency_field="currency_id",
                                    compute="_compute_costs", store=True)
    roi = fields.Float("ROI (%)", compute="_compute_roi", store=True)

    @api.depends("trip_ids")
    def _compute_trip_count(self):
        for v in self:
            v.trip_count = len(v.trip_ids)

    @api.depends("trip_ids.revenue", "trip_ids.fuel_consumed", "maintenance_ids.cost")
    def _compute_costs(self):
        fp = float(self.env["ir.config_parameter"].sudo().get_param(
            "transitops.fuel_price_per_litre", "1.50"))
        for v in self:
            v.total_revenue = sum(v.trip_ids.mapped("revenue"))
            v.total_fuel_cost = sum(v.trip_ids.mapped("fuel_consumed")) * fp
            v.total_maintenance_cost = sum(v.maintenance_ids.mapped("cost"))

    @api.depends("total_revenue", "total_maintenance_cost", "total_fuel_cost", "acquisition_cost")
    def _compute_roi(self):
        for v in self:
            if v.acquisition_cost:
                net = v.total_revenue - (v.total_maintenance_cost + v.total_fuel_cost)
                v.roi = (net / v.acquisition_cost) * 100
            else:
                v.roi = 0.0

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
