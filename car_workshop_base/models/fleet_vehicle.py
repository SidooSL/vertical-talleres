###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product Ref.',
        ondelete='restrict',
    )

    @api.model
    def create(self, data):
        re = super().create(data)
        product = self.env['product.product'].create({
            'name': re.display_name,
            'purchase_ok': False,
            'sale_ok': False,
            'tracking': 'none',
            'type': 'product',
        })
        re.product_id = product
        move = self.env['stock.move'].create({
            'location_id': self.env.ref('stock.location_inventory').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'name': ''.join(('INV: ', product.display_name)),
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': 1.0,
            'state': 'done',
        })
        self.env['stock.move.line'].create({
            'location_id': move.location_id.id,
            'location_dest_id': move.location_dest_id.id,
            'move_id': move.id,
            'product_id': product.id,
            'product_uom_id': product.uom_id.id,
            'qty_done': 1.0,
        })
        return re
