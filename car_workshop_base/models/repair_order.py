###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import _, api, fields, models
from datetime import datetime, timedelta
from odoo.tools import html2plaintext


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    def _default_validity_date(self):
        if self.env['ir.config_parameter'].sudo().get_param(
                'sale.use_quotation_validity_days'):
            days = self.env.company.quotation_validity_days
            if days > 0:
                return fields.Date.to_string(datetime.now() + timedelta(days))
        return False

    product_id = fields.Many2one(
        'product.product', string='Product to Repair',
        domain="[('type', 'in', ['product', 'consu']), '|', "
               "('company_id', '=', company_id), "
               "('company_id', '=', False)]",
        readonly=True, required=False,
        states={'draft': [('readonly', False)]},
        check_company=True)
    product_uom = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',
        compute='_compute_product_uom', store=True, precompute=True,
        readonly=True, required=False,
        states={'draft': [('readonly', False)]},
        domain="[('category_id', '=', product_uom_category_id)]")
    address_id = fields.Many2one(
        'res.partner', string='Address',
        help='Who picks it up? Who should it be sent to?',
        readonly=True, states={'draft': [('readonly', False)]},
        domain="[('parent_id', '=', partner_id)]",
        check_company=True)
    arrival_date = fields.Datetime(
        string='Arrival Date',
        help='The arrival date of the vehicle.',
        default=datetime.now(),
    )
    child_ids = fields.One2many(
        comodel_name='repair.order',
        inverse_name='parent_id',
    )
    company_currency = fields.Many2one(
        readonly=True,
        related='company_id.currency_id',
        string='Company Currency',
    )
    date_deadline = fields.Datetime(
        string='Date Deadline',
        help='The deadline date of the vehicle.',
    )
    fault_notes = fields.Text(
        string='Fault Notes',
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
    odometer = fields.Integer(
        related='vehicle_id.odometer',
    )
    new_odometer = fields.Integer(
        default=False,
        string='New Odometer',
        tracking=True,
    )
    parent_id = fields.Many2one(
        comodel_name='repair.order',
        domain='[(\'id\', \'!=\', active_id)]',
        string='RO Parent',
    )
    partner_id = fields.Many2one(
        help='Customer to whom the repair is opened.',
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
    validity_date = fields.Date(
        string='Expiration',
        copy=False,
        default=_default_validity_date,
    )
    vehicle_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehicle',
    )

    @api.onchange('arrival_date')
    def _onchange_arrival_date(self):
        if self.arrival_date:
            self.date_deadline = self.arrival_date + timedelta(days=2)

    @api.onchange('new_odometer')
    def _onchange_new_odometer(self):
        if not self.new_odometer:
            return
        if not self.vehicle_id:
            return
        if self.odometer == self.new_odometer:
            return
        if not self.odometer > self.new_odometer:
            self.vehicle_id.write({'odometer': self.new_odometer})
        else:
            msg = _(''' The last odometer (%s) cannot be greater than the new
             one (%s).\n %s >> %s ''') % (
                self.odometer,
                self.new_odometer,
                self.odometer,
                self.new_odometer,
            )
            return {'warning': {
                'tittle': _('Warning'),
                'message': msg
            }}

    @api.depends('child_ids')
    def _compute_subords_count(self):
        for order in self:
            order.subords_count = len(order.child_ids)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super().onchange_partner_id()
        if self.partner_id and self.vehicle_id:
            self.partner_invoice_id = self.vehicle_id.partner_invoice_id
            self.address_id = False

    @api.onchange('repair_type')
    def _onchange_repair_type(self):
        if self.repair_type == 'other':
            self.vehicle_id = False
            self.arrival_date = False
            self.date_deadline = False
            self.odometer = False
            self.new_odometer = False
            self.fuel = False
            self.is_blocked_to_drive = False
            self.is_damaged = False

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            self.partner_id = self.vehicle_id.driver_id
            self.product_id = self.vehicle_id.product_id
            self.repair_type = 'vehicle_repair'

    def _create_invoices(self, group=False, show_repair_note=True, show_origin_section=True):
        moves = super()._create_invoices(group)

        if show_origin_section or show_repair_note:
            repairs = list(
                self.env['repair.order'].search(
                    [['id', 'in', list(moves.keys())]]
                )
            )
            invoices = self.env['account.move'].search(
                [['id', 'in', list(moves.values())]]
            )

            for invoice in invoices:
                line_names = [line.name for line in invoice.invoice_line_ids]
                invoice_repairs = repairs.copy()
                if not group:
                    for repair in repairs:
                        if repair.name != invoice.invoice_origin:
                            invoice_repairs.remove(repair)

                i = 0
                new_lines = 0
                while i < len(invoice.invoice_line_ids) - new_lines:
                    for repair in invoice_repairs:
                        if not group or repair.name in line_names[i]:
                            if show_origin_section:
                                invoice.write({
                                    'invoice_line_ids':  [(0, 0, {
                                        'name': repair.name,
                                        'display_type': 'line_section',
                                        'sequence': i + new_lines + 1,
                                    })]})
                                new_lines = new_lines + 1
                            if show_repair_note and repair.quotation_notes:
                                invoice.write({
                                    'invoice_line_ids':  [(0, 0, {
                                        'name': html2plaintext(repair.quotation_notes),
                                        'display_type': 'line_note',
                                        'sequence': i + new_lines + 1,
                                    })]})
                                new_lines = new_lines + 1
                            repairs.remove(repair)
                            invoice_repairs.remove(repair)
                    invoice.invoice_line_ids[i].write({'sequence': i+new_lines+1})
                    i = i + 1
                    invoice.write({'narration': ''})
        return moves
