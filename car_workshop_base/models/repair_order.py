###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    invoice_method = fields.Selection(
        default='b4repair',
    )
    location_id = fields.Many2one(
        required=False,
    )
    product_id = fields.Many2one(
        required=False,
    )
    product_qty = fields.Float(
        required=False,
    )
    tracking = fields.Selection(
        default='none',
    )
    vehicle_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehicle',
    )
