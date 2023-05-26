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
    'depends': ['account', 'sale', 'purchase', 'stock'],
    'data': [
        'report/sale_order_inherit.xml',
        'report/tax_credit_invoice_view.xml',
        'report/tax_credit_invoice_with_payments_view.xml',
        'report/receipt_purchase_order.xml',
        'report/receipt_application_purchase.xml',
        'report/receipt_stock_picking.xml',
        'report/stock_picking_invoice.xml',
    ],
    
    'demo': [],
    'test': [],
    "images": ["static/description/",],
    "application": False,
    
}
