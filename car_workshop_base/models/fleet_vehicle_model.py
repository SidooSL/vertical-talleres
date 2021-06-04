###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, models


class FleetVehicleModel(models.Model):
    _inherit = 'fleet.vehicle.model'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        return self.search(
            ['|',
             ('brand_id.name', operator, name),
             ('name', operator, name)] + (args or []),
            limit=limit).name_get()
