###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    invoice_method = fields.Selection(
        default='b4repair',
    )
    product_qty = fields.Float(
        default=1.0,
    )
    repair_type = fields.Selection(
        [
            ('vehicle_repair', 'Vehicle Repair'),
            ('other', 'Other'),
        ],
        default='vehicle_repair',
        string='Repair Type',
    )
    vehicle_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehicle',
    )

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            self.product_id = self.vehicle_id.product_id
            self.repair_type = 'vehicle_repair'
