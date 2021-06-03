###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import _, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def button_contact_vehicles(self):
        return{
            'name': _('Vehicles'),
            'view_mode': 'tree,form',
            'res_model': 'fleet.vehicle',
            'type': 'ir.actions.act_window',
            'domain': [('customer_id', '=', self.id)],
            'context': {
                'default_customer_id': self.id,
            },
        }
