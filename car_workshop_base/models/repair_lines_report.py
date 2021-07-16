###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import tools, fields, models
from odoo.addons import decimal_precision as dp


class RepairLinesReport(models.Model):
    _name = 'repair.lines.report'
    _description = 'Repair Lines and Fees Report'
    _order = 'repair_id'
    _auto = False

    name = fields.Text(
        string='Description',
        readonly=True,
    )
    repair_id = fields.Many2one(
        comodel_name='repair.order',
        string='Repair Order Reference',
        readonly=True,
    )
    repair_type = fields.Selection(
        [
            ('line', 'Line'),
            ('fee', 'Fee'),
        ],
        string='Repair Type',
        readonly=True,
    )
    type = fields.Selection(
        [
            ('add', 'Add'),
            ('remove', 'Remove'),
        ],
        string='Type',
        readonly=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        readonly=True,
    )
    product_uom_qty = fields.Float(
        string='Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True,
    )
    price_unit = fields.Float(
        string='Unit Price',
        digits=dp.get_precision('Product Price'),
        readonly=True,
    )
    price_subtotal = fields.Float(
        string='Subtotal',
        digits=0,
        readonly=True,
    )
    lot_id = fields.Many2one(
        comodel_name='stock.production.lot',
        string='Lot/Serial',
        readonly=True,
    )

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ('WITH %s' % with_clause) if with_clause else ''

        rl_select_ = '''
            rl.id as id,
            'line' as repair_type,
            rl.name as name,
            rl.product_id as product_id,
            rl.repair_id as repair_id,
            rl.type as type,
            rl.lot_id as lot_id,
            rl.product_uom_qty as product_uom_qty,
            rl.price_unit as price_unit,
            rl.price_subtotal as price_subtotal
        '''

        rf_select_ = '''
            -rf.id as id,
            'fee' as repair_type,
            rf.name as name,
            rf.product_id as product_id,
            rf.repair_id as repair_id,
            '' as type,
            0 as lot_id,
            rf.product_uom_qty as product_uom_qty,
            rf.price_unit as price_unit,
            rf.price_subtotal as price_subtotal
        '''

        return '''%s (SELECT %s FROM repair_line rl
                      UNION ALL SELECT %s FROM repair_fee rf)
               ''' % (with_, rl_select_, rf_select_)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            'CREATE or REPLACE VIEW %s as (%s)' % (self._table, self._query()))
