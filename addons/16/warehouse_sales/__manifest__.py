# -*- coding: utf-8 -*-
##############################################################################
{
    'name': 'Warehouse on INVOICE',
    'version': '14.0.1.0',
    'category': '# TODO',
    'author': 'Astratech',
    'license': 'AGPL-3',
    'website': 'http://astratech.com.do',
    'depends': [
        'account',
        'sale_stock',
    ],
    'data': [
        "views/account/account_move_views.xml",
    ],
    'demo': [],
    'installable': True,
    'active': False,
    'application': True,
    'qweb': [],
}