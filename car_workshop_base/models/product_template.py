###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    vehicle_brand_id = fields.Many2one(
        comodel_name='fleet.vehicle.model.brand',
        string='Vehicle Brand',
    )
