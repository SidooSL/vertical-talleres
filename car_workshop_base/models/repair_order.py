###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    company_currency = fields.Many2one(
        readonly=True,
        relation='res.currency',
        related='company_id.currency_id',
        string='Currency',
    )
    invoice_method = fields.Selection(
        default='b4repair',
    )
    is_blocked_to_drive = fields.Boolean(
        string='Is blocked to drive?',
    )
    is_damaged = fields.Boolean(
        string='Is damaged?',
    )
    name = fields.Char(
        readonly=True,
        required=False,
        default='',
    )
    parent_id = fields.Many2one(
        comodel_name='repair.order',
        domain='[(\'id\', \'!=\', active_id)]',
        string='OR Parent',
    )
    product_qty = fields.Float(
        default=1.0,
    )
    planned_revenue = fields.Monetary(
        currency_field='company_currency',
        string='Expected Revenue',
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

    @api.model
    def create(self, values):
        res = super().create(values)
        res['name'] = self.env['ir.sequence'].next_by_code('repair.order')
        return res

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            self.partner_id = self.vehicle_id.customer_id
            self.product_id = self.vehicle_id.product_id
            self.repair_type = 'vehicle_repair'
