# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Change Effective Date',
    'author': 'Jeffry J. De La Rosa',
    'version': '15.0.2.0.0',
    'summary': 'Change Effective Date in Stock Picking',
    'license': 'OPL-1',
    'sequence': 1,
    'description': """Allows You Changing Effective Date of DO, RO, Internal and All Inventory Transfers""",
    'category': 'Inventory',
    'website': 'https://www.altela.net',
    'price':'35',
    'currency':'USD',
    'depends': [
        'account',
        'purchase',
        'sale_stock',
        'sale_management',
        'stock_account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/effective_date_change.xml',
        'wizard/change_effective_wizard_views.xml',
        'views/sale_order.xml',
        'views/stock_quant.xml',

    ],
    'images': [
        'static/description/assets/banner.gif',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'pre_init_hook': 'pre_init_check',
}