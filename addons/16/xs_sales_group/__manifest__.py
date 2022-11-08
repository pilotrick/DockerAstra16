# -*- coding: utf-8 -*-
{
    'name': 'Sale Advance Payment Groups rules',
    'category': 'Sales',
    'summary': """Display to group users
    """,
    'description': '''Assign access rights groups to users''',
    'license': 'OPL-1',
    'version': '1.1',
    'author': 'Malik Zohaib',
    'depends': ['xs_sale_advance_payment', 'sale','dev_customer_credit_limit'],
    'data': [
             'security/sales_security.xml',
             'views/sale_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
