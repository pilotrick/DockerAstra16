# -*- encoding: UTF-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015-Today Laxicon Solution.
#    (<http://laxicon.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################


{
    'name': "Purchase Order Line View",
    'version': '1.0.1',
    'summary': """Purchase View""",
    "author": "Astratech",
    'website': 'http://laxicon.in/',
    "license":  "LGPL-3",
    'category': 'purchase',
    'description': """
This modual help you to explore Purchase Order Line with tree, kanban, paovet, graph, calendar View.
    """,
    'depends': [
        'purchase'
    ],

    'data': [
        'security/purchase_order_group.xml',
        'views/purchase_view.xml',
    ],
    'images':  ["static/description/banner.png"],
    "application":  False,
    "installable":  True,
    "auto_install":  False,
    "pre_init_hook":  "pre_init_check",
}
