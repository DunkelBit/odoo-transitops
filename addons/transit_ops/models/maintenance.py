from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Maintenance(models.Model):
    _name = "transitops.maintenance"
    _description = "Maintenance Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc"

    name = fields.Char("Reference", required=True, readonly=True, default="New")
    vehicle_id = fields.Many2one("transitops.vehicle", "Vehicle", required=True, tracking=True)
    maintenance_type = fields.Selection([
        ("preventive", "Preventive"),
        ("corrective", "Corrective"),
        ("emergency", "Emergency"),
    ], string="Type", default="preventive", required=True)

    description = fields.Text("Notes")
    cost = fields.Monetary("Cost", currency_field="currency_id")
    currency_id = fields.Many2one("res.currency",
                                  default=lambda self: self.env.company.currency_id)

    date_start = fields.Date("Started", required=True)
    date_end = fields.Date("Finished")
    status = fields.Selection([
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ], default="scheduled", required=True, tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "transitops.maintenance") or "New"
        return super().create(vals_list)

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for m in self:
            if m.date_start and m.date_end and m.date_end < m.date_start:
                raise ValidationError("End date can't be before start date.")

    def action_start(self):
        for m in self:
            m.status = "in_progress"
            m.vehicle_id.status = "in_shop"

    def action_complete(self):
        for m in self:
            m.status = "completed"
            m.date_end = fields.Date.context_today(self)

            # check if vehicle has other active maintenance work
            other_active = self.search([
                ("vehicle_id", "=", m.vehicle_id.id),
                ("id", "!=", m.id),
                ("status", "=", "in_progress"),
            ])
            if not other_active:
                m.vehicle_id.status = "available"
