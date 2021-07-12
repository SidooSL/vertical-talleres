###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import re


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    acquisition_date = fields.Date(
        required=True,
    )
    driver_id = fields.Many2one(
        string='Owner',
        required=True,
    )
    last_mot = fields.Date(
        string='Last MOT',
    )
    license_plate = fields.Char(
        required=True,
    )
    odometer = fields.Float(
        track_visibility='always',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product Ref.',
        ondelete='restrict',
    )
    model_version = fields.Char(
        string='Model Version',
        required=True,
    )
    next_mot = fields.Date(
        string='Next MOT',
    )
    partner_invoice_id = fields.Many2one(
        comodel_name='res.partner',
        string='Invoice address',
        required=True,
    )
    vin_sn = fields.Char(
        required=True,
    )

    @api.one
    @api.constrains('license_plate')
    def _check_license_plate(self):
        if not re.fullmatch('[0-9A-Z]+', self.license_plate):
            raise ValidationError(_('The license plate only accepts'
                                    ' alphanumeric caps characters.'))

    @api.one
    @api.constrains('vin_sn')
    def _check_vin_sn(self):
        if not re.fullmatch('[0-9A-Z]{17}', self.vin_sn):
            raise ValidationError(_('The vin number needs to have 17'
                                    ' alphanumeric caps characters.'))

    @api.onchange('driver_id')
    def _onchange_driver_id(self):
        if self.driver_id:
            self.partner_invoice_id = self.driver_id

    @api.onchange('last_mot')
    def _onchange_last_mot(self):
        if self.last_mot:
            self.next_mot = self.last_mot.replace(year=self.last_mot.year + 1)

    @api.model
    def create(self, data):
        rec = super().create(data)
        product = self.env['product.product'].create({
            'name': rec.display_name,
            'purchase_ok': False,
            'sale_ok': False,
            'tracking': 'none',
            'type': 'product',
        })
        rec.product_id = product
        move = self.env['stock.move'].create({
            'location_id': self.env.ref('stock.location_inventory').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'name': ''.join(('INV: ', product.display_name)),
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': 1.0,
            'state': 'done',
        })
        self.env['stock.move.line'].create({
            'location_id': move.location_id.id,
            'location_dest_id': move.location_dest_id.id,
            'move_id': move.id,
            'product_id': product.id,
            'product_uom_id': product.uom_id.id,
            'qty_done': 1.0,
        })
        return rec

    def button_vehicle_repair_lines_report(self):
        return{
            'name': _('Operations & Fees'),
            'view_mode': 'tree',
            'res_model': 'repair.lines.report',
            'type': 'ir.actions.act_window',
            'domain': [('repair_id', 'in', self.repair_ids.ids)],
        }
