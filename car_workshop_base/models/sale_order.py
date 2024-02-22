###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_invoices(self, grouped=False, final=False, date=None, show_origin_section=True):
        invoices = super(SaleOrder, self)._create_invoices(grouped, final, date)

        if show_origin_section:
            for invoice in invoices:
                invoice_lines = invoice.invoice_line_ids
                order_lines_by_order = {}

                for line in invoice_lines:
                    if line.sale_line_ids:
                        order_id = line.sale_line_ids[0].order_id.id
                        order_lines_by_order.setdefault(order_id, []).append(line)

                next_sequence = 1
                for order_id, order_lines in order_lines_by_order.items():
                    order = self.env['sale.order'].browse(order_id)
                    section_name = order.name
                    section_line = (0, 0, {
                        'name': section_name,
                        'display_type': 'line_section',
                        'sequence': next_sequence,
                    })
                    next_sequence += 1
                    lines_to_update = []
                    for line in order_lines:
                        lines_to_update.append((1, line.id, {'sequence': next_sequence}))
                        next_sequence += 1
                    invoice.write({'invoice_line_ids': [section_line] + lines_to_update})

        return invoices
