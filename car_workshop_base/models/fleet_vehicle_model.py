###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class FleetVehicleModel(models.Model):
    _inherit = 'fleet.vehicle.model'

    vehicle_type = fields.Selection(
        selection_add=[
            ('machinery', 'Machinery'),
            ('motorcycle', 'Motorcycle'),
            ('tractor', 'Tractor'),
        ],
        ondelete={
            'machinery': 'cascade',
            'motorcycle': 'cascade',
            'tractor': 'cascade',
        },
    )

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        return self.search(
            ['|',
             ('brand_id.name', operator, name),
             ('name', operator, name)] + (args or []),
            limit=limit).name_get()
