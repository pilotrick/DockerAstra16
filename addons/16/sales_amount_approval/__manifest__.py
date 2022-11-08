# -*- coding: utf-8 -*-
{
    'name': 'Sales Amount Approval',
    'category': 'Sales',
    'summary': """Asks permission from user to confirm if amounts of sales are under 6000$ 
    """,
    'description': '''Permission on confirm ''',
    'license': 'OPL-1',
    'version': '1.5',
    'author': 'Malik Zohaib',
    'depends': ['sale','dev_customer_credit_limit'],
    'data': [
            'security/ir.model.access.csv',
            'security/sales_security.xml',
             'views/res_users.xml',
             'views/sale_order.xml',
             'views/sale_config_settings.xml',
             'views/sales_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
