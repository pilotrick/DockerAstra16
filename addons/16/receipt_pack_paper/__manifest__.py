# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Receipt International pack & paper',
    'version': '16.1.0',
    'category': 'Reporting',
    'author': 'Astratech',
    'website': 'http://IPPDR.com',
    'summary': """
    	Receipt International Pack & Paper
    """,
    'description' : """
       This module prints a Invoice personalized of International Pack & Paper.
    """,
    'depends': ['account', 'sale', 'purchase'],
    'data': [
        'report/sale_order_inherit.xml',
        'report/tax_credit_invoice_view.xml',
        'report/receipt_purchase_order.xml',
        'report/receipt_application_purchase.xml',
    ],
    
    'demo': [],
    'test': [],
    "images": ["static/description/",],
    "application": False,
    
}
