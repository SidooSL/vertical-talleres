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
    'name': 'Car Workshop Installer',
    'summary': 'Install necesary modules for Car Worshop frame.',
    'author': 'Óscar Soto Ochoa, Jorge Quinteros, Alberto Martínez Rodríguez, '
              'SDi Soluciones Informáticas',
    'website': 'https://sdi.es/odoo/',
    'license': 'AGPL-3',
    'category': 'Workshop',
    'version': '14.0.1.0.0',
    'depends': [
        'board',
        'car_workshop_base',
        'calendar',
        'contacts',
        'fleet_search_customize',
        'l10n_es',
        'l10n_es_toponyms',
        'l10n_es_partner',
        'partner_filter_general',
        'web_responsive',
        'web_tree_many2one_clickable',
    ],
}
