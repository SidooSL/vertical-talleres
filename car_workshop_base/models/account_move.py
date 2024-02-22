###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    repair_order_count = fields.Integer(
        compute="_compute_origin_ro_count",
        string='Repair Order Count',
    )

    @api.depends('line_ids.repair_line_ids')
    def _compute_origin_ro_count(self):
        for move in self:
            move.repair_order_count = len(move.line_ids.repair_line_ids.repair_id)

    def action_view_source_repair_orders(self):
        self.ensure_one()
        source_orders = self.line_ids.repair_line_ids.repair_id
        result = self.env['ir.actions.act_window']._for_xml_id('repair.action_repair_order_tree')
        if len(source_orders) > 1:
            result['domain'] = [('id', 'in', source_orders.ids)]
        elif len(source_orders) == 1:
            result['views'] = [(self.env.ref('repair.view_repair_order_form', False).id, 'form')]
            result['res_id'] = source_orders.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
