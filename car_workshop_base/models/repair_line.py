###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class RepairLine(models.Model):
    _inherit = 'repair.line'

    product_id = fields.Many2one(
        domain=[('type', 'in', ['consu', 'product'])],
    )
