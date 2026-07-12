from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Maintenance(models.Model):
    _name = "transitops.maintenance"
    _description = "Maintenance Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc"

    name = fields.Char(string="Reference", required=True, readonly=True, default="New")
    vehicle_id = fields.Many2one(
        "transitops.vehicle",
        string="Vehicle",
        required=True,
        tracking=True,
    )
    maintenance_type = fields.Selection(
        [
            ("preventive", "Preventive"),
            ("corrective", "Corrective"),
            ("emergency", "Emergency"),
        ],
        string="Type",
        required=True,
        default="preventive",
    )
    description = fields.Text(string="Description")
    cost = fields.Monetary(
        string="Cost",
        currency_field="currency_id",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )
    date_start = fields.Date(string="Start Date", required=True)
    date_end = fields.Date(string="End Date")
    status = fields.Selection(
        [
            ("scheduled", "Scheduled"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
        ],
        string="Status",
        default="scheduled",
        required=True,
        tracking=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "transitops.maintenance"
                ) or "New"
        return super().create(vals_list)

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_end < rec.date_start:
                raise ValidationError("End date cannot be before start date.")

    def action_start(self):
        for rec in self:
            rec.status = "in_progress"
            rec.vehicle_id.status = "in_shop"

    def action_complete(self):
        for rec in self:
            rec.status = "completed"
            rec.date_end = fields.Date.context_today(self)
            has_other_active = self.search(
                [
                    ("vehicle_id", "=", rec.vehicle_id.id),
                    ("id", "!=", rec.id),
                    ("status", "=", "in_progress"),
                ]
            )
            if not has_other_active:
                rec.vehicle_id.status = "available"
