###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from collections import defaultdict
from datetime import datetime, timedelta


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    def _default_validity_date(self):
        if self.env['ir.config_parameter'].sudo().get_param(
                'sale.use_quotation_validity_days'):
            days = self.env.company.quotation_validity_days
            if days > 0:
                return fields.Date.to_string(datetime.now() + timedelta(days))
        return False

    address_id = fields.Many2one(
        help='Who picks it up? Who should it be sent to?',
    )
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

    @api.constrains('new_odometer')
    def _check_new_odometer(self):
        if self.vehicle_id and self.new_odometer <= 0:
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

    def _create_invoices(self, group=False):
        """ Creates invoice(s) for repair order.
        @param group: It is set to true when group invoice is to be generated.
        @return: Invoice Ids.
        """
        grouped_invoices_vals = {}
        repairs = self.filtered(lambda repair: repair.state not in ('draft', 'cancel')
                                               and not repair.invoice_id
                                               and repair.invoice_method != 'none')
        for repair in repairs:
            repair = repair.with_company(repair.company_id)
            partner_invoice = repair.partner_invoice_id or repair.partner_id
            if not partner_invoice:
                raise UserError(_('You have to select an invoice address in the repair form.'))

            narration = repair.quotation_notes
            currency = repair.pricelist_id.currency_id
            company = repair.env.company

            journal = repair.env['account.move'].with_context(move_type='out_invoice')._get_default_journal()
            if not journal:
                raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (company.name, company.id))

            if (partner_invoice.id, currency.id, company.id) not in grouped_invoices_vals:
                grouped_invoices_vals[(partner_invoice.id, currency.id, company.id)] = []
            current_invoices_list = grouped_invoices_vals[(partner_invoice.id, currency.id, company.id)]

            if not group or len(current_invoices_list) == 0:
                fpos = self.env['account.fiscal.position'].get_fiscal_position(partner_invoice.id, delivery_id=repair.address_id.id)
                invoice_vals = {
                    'move_type': 'out_invoice',
                    'partner_id': partner_invoice.id,
                    'partner_shipping_id': repair.address_id.id,
                    'currency_id': currency.id,
                    'narration': narration,
                    'invoice_origin': repair.name,
                    'repair_ids': [(4, repair.id)],
                    'invoice_line_ids': [],
                    'fiscal_position_id': fpos.id
                }
                if partner_invoice.property_payment_term_id:
                    invoice_vals['invoice_payment_term_id'] = partner_invoice.property_payment_term_id.id
                current_invoices_list.append(invoice_vals)
            else:
                # if group == True: concatenate invoices by partner and currency
                invoice_vals = current_invoices_list[0]
                invoice_vals['invoice_origin'] += ', ' + repair.name
                invoice_vals['repair_ids'].append((4, repair.id))
                if not invoice_vals['narration']:
                    invoice_vals['narration'] = narration
                else:
                    invoice_vals['narration'] += '\n' + narration

            # Create invoice line section
            invoice_line_vals = {
                'name': repair.name,
                'display_type': 'line_section',
            }
            invoice_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))
            # Create invoice line note
            invoice_line_vals = {
                'name': repair.internal_notes,
                'display_type': 'line_note',
            }
            invoice_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))
            # Create invoice lines from operations.
            for operation in repair.operations.filtered(lambda op: op.type == 'add'):
                name = operation.name

                account = operation.product_id.product_tmpl_id._get_product_accounts()['income']
                if not account:
                    raise UserError(_('No account defined for product "%s".', operation.product_id.name))

                invoice_line_vals = {
                    'name': name,
                    'account_id': account.id,
                    'quantity': operation.product_uom_qty,
                    'tax_ids': [(6, 0, operation.tax_id.ids)],
                    'product_uom_id': operation.product_uom.id,
                    'price_unit': operation.price_unit,
                    'product_id': operation.product_id.id,
                    'repair_line_ids': [(4, operation.id)],
                }

                if currency == company.currency_id:
                    balance = -(operation.product_uom_qty * operation.price_unit)
                    invoice_line_vals.update({
                        'debit': balance > 0.0 and balance or 0.0,
                        'credit': balance < 0.0 and -balance or 0.0,
                    })
                else:
                    amount_currency = -(operation.product_uom_qty * operation.price_unit)
                    balance = currency._convert(amount_currency, company.currency_id, company, fields.Date.today())
                    invoice_line_vals.update({
                        'amount_currency': amount_currency,
                        'debit': balance > 0.0 and balance or 0.0,
                        'credit': balance < 0.0 and -balance or 0.0,
                        'currency_id': currency.id,
                    })
                invoice_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))

            # Create invoice lines from fees.
            for fee in repair.fees_lines:
                name = fee.name

                if not fee.product_id:
                    raise UserError(_('No product defined on fees.'))

                account = fee.product_id.product_tmpl_id._get_product_accounts()['income']
                if not account:
                    raise UserError(_('No account defined for product "%s".', fee.product_id.name))

                invoice_line_vals = {
                    'name': name,
                    'account_id': account.id,
                    'quantity': fee.product_uom_qty,
                    'tax_ids': [(6, 0, fee.tax_id.ids)],
                    'product_uom_id': fee.product_uom.id,
                    'price_unit': fee.price_unit,
                    'product_id': fee.product_id.id,
                    'repair_fee_ids': [(4, fee.id)],
                }

                if currency == company.currency_id:
                    balance = -(fee.product_uom_qty * fee.price_unit)
                    invoice_line_vals.update({
                        'debit': balance > 0.0 and balance or 0.0,
                        'credit': balance < 0.0 and -balance or 0.0,
                    })
                else:
                    amount_currency = -(fee.product_uom_qty * fee.price_unit)
                    balance = currency._convert(amount_currency, company.currency_id, company,
                                                fields.Date.today())
                    invoice_line_vals.update({
                        'amount_currency': amount_currency,
                        'debit': balance > 0.0 and balance or 0.0,
                        'credit': balance < 0.0 and -balance or 0.0,
                        'currency_id': currency.id,
                    })
                invoice_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))

        # Create invoices.
        invoices_vals_list_per_company = defaultdict(list)
        for (partner_invoice_id, currency_id, company_id), invoices in grouped_invoices_vals.items():
            for invoice in invoices:
                invoices_vals_list_per_company[company_id].append(invoice)

        for company_id, invoices_vals_list in invoices_vals_list_per_company.items():
            # VFE TODO remove the default_company_id ctxt key ?
            # Account fallbacks on self.env.company, which is correct with with_company
            self.env['account.move'].with_company(company_id).with_context(default_company_id=company_id, default_move_type='out_invoice').create(invoices_vals_list)

        repairs.write({'invoiced': True})
        repairs.mapped('operations').filtered(lambda op: op.type == 'add').write({'invoiced': True})
        repairs.mapped('fees_lines').write({'invoiced': True})

        return dict((repair.id, repair.invoice_id.id) for repair in repairs)
