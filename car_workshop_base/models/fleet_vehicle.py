###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class Vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    customer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        required=True,
    )
