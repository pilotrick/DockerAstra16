# -*- coding: utf-8 -*-
###########################################################################
#
#    @author Xpath Solutions <xpathsolution@gmail.com>
#
###########################################################################

{
    'name': 'Sale Advance Payment',
    'category': 'Sales',
    'summary': """Make advance payment in Sales
        sales advance payment sale advance payment advance sales payment advance so payment
    """,
    'description': '''Advance payments in Sales and then use in Invoices''',
    'license': 'OPL-1',
    'version': '1.0',
    'author': 'Xpath Solutions',
    'depends': ['sale_management', 'account'],
    'data': ['wizard/sale_advance_payment_wizard.xml',
             'views/sale_view.xml',
             'security/ir.model.access.csv'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 19.99,
    'currency': 'EUR',
    'images': ['static/description/banner.jpg'],
}
