# -*- coding: utf-8 -*-
{
    'name': 'Cancel Stock Landed Cost in Odoo',
    'version': '14.0.0.0',
    'category': 'Inventory',
    "license": "OPL-1",
    'summary': 'Cancel and Reset Stock Landed Cost in Odoo Reverse stock landed cost Recalculate stock landed cost',
    'description': """

        """,
    'website': 'https://astratech.com.do',
    'author': 'Astra Tech SRL',
    'depends': ['base','stock_landed_costs'],
    'data': [
             'views/astratech_inherit_landed_cost.xml',
    ],
    'installable': True,
    'auto_install': False,
}
