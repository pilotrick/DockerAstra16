# -*- coding: utf-8 -*-
{
    'name': 'Sales Commission Generic',
    'category': 'Sales',
    'summary': """Fields in Invoice
    """,
    'description': '''invoice date, due date,payment''',
    'license': 'OPL-1',
    'version': '1.1',
    'author': 'Malik Zohaib',
    'depends': ['sales_commission_generic', 'sale'],
    'data': [
             'views/account_view.xml',
             'views/sales_commission.xml',
             'report/sale_inv_comm_template.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
