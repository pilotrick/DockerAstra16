# -*- coding: utf-8 -*-
{
    'name': 'Advanced Down Payment',
    'version': '14.0.1.0',
    'license': 'Other proprietary',
    'category': 'Sales',
    'summary': """This module provides feature to add flexible downpayment from sale order. User will be able to distribute down payment amount 
                    with different taxes.
                """,
    'author':'Craftsync Technologies',
    'maintainer': 'Craftsync Technologies',
    'website': 'https://www.craftsync.com/',
    'license': 'OPL-1',
    'support':'info@craftsync.com',
    'sequence': 1,
    'depends': [
        'account', 'sale_management'
    ],
    
    'data': [
        'views/sale_advance_payment_inv_views.xml',
        'security/ir.model.access.csv'
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/main_screen.png'],
    'price': 99.00,
    'currency': 'EUR',
}

