###############################################################################
#
#    SDi Soluciones Digitales
#    Copyright (C) 2021-Today SDi Soluciones Digitales <www.sdi.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
{
    'name': 'Car Workshop Base',
    'summary': 'Car workshop base module.',
    'author': 'Óscar Soto Ochoa, Valentín Georgian Castravete,'
              ' SDi Soluciones Digitales',
    'website': 'https://sdi.es/odoo/',
    'license': 'AGPL-3',
    'category': 'Workshop',
    'version': '14.0.1.0.0',
    'depends': [
        'fleet',
        'repair',
        'sale',
    ],
    'data': [
        'data/brand_data.xml',
        'security/car_workshop_security.xml',
        'security/ir.model.access.csv',
        # 'report/repair_reports.xml',
        'report/repair_templates_vehicle_repair_order.xml',
        'report/report_repairorder.xml',
        'views/car_workshop_menu_views.xml',
        'views/fleet_vehicle.xml',
        'views/product_template.xml',
        'views/repair_lines_report.xml',
        'views/repair_order.xml',
        'views/res_partner.xml',
    ],
    'application': True,
}
