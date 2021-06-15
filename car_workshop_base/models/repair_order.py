###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    arrival_date = fields.Datetime(
        string='Arrival Date',
        required=True,
        help='The arrival date of the vehicle.'
    )
    child_ids = fields.One2many(
        comodel_name='repair.order',
        inverse_name='parent_id',
    )
    company_currency = fields.Many2one(
        readonly=True,
        relation='res.currency',
        related='company_id.currency_id',
        string='Currency',
    )
    fuel = fields.Integer(
        string='Fuel (%)',
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
    odometer = fields.Float(
        related='vehicle_id.odometer',
    )
    new_odometer = fields.Float(
        default=False,
        string='New Odometer',
        track_visibility='onchange',
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
    subords_count = fields.Integer(
        string='SubOrds Count',
        compute='_compute_subords_count',
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

    @api.constrains('new_odometer')
    def _check_last_odometer(self):
        if self.new_odometer <= 0:
            raise ValidationError(_(
                'You cannot set the odometer to 0. Please, set it.'))
        return True

    @api.onchange('new_odometer')
    def _onchange_new_odometer(self):
        if not self.new_odometer:
            return
        if not self.vehicle_id:
            return
        if self.odometer == self.new_odometer:
            return
        if self.odometer > self.new_odometer:
            msg = _(''' The last odometer (%s) cannot be greater than the new
             one (%s).\n %s >> %s ''' % (
                self.odometer,
                self.new_odometer,
                self.odometer,
                self.new_odometer,
            ))
            return {'warning': {
                'tittle': _('Warning'),
                'message': msg
            }}
        self.vehicle_id.write({'odometer': self.new_odometer})

    @api.depends('child_ids')
    def _compute_subords_count(self):
        if self.child_ids:
            self.subords_count = len(self.child_ids)

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            self.partner_id = self.vehicle_id.partner_id
            self.product_id = self.vehicle_id.product_id
            self.repair_type = 'vehicle_repair'
