###############################################################################
#
#    SDi Soluciones Informáticas
#    Copyright (C) 2021-Today SDi Soluciones Informáticas <www.sdi.es>
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
    'name': 'Repair View Customize',
    'summary': '''
        Replaces the product_id field with the vehicle_id field on the Repair
        View, and adds a triple field search
    ''',
    'author': 'Alberto Martínez Rodríguez, SDi Soluciones Informáticas',
    'website': 'https://sdi.es/odoo/',
    'license': 'AGPL-3',
    'category': 'Workshop',
    'version': '14.0.1.0.0',
    'depends': [
        'repair',
    ],
    'data': [
        'views/repair_view_customize.xml',
    ]
}
