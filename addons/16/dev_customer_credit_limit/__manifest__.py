# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Customer Credit Limit',
    'version': '14.0.1.1',
    'sequence': 1,
    'category': 'Generic Modules/Accounting',
    'description':
        """
odoo Apps will check the Customer Credit Limit on Sale order and notify to the sales manager,
 
    """,
    'summary': 'odoo Apps will check the Customer Credit Limit on Sale order and notify to the sales manager',
    'author': 'Devintelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',
    'images': ['images/main_screenshot.png'],
    'depends': ['sale_management', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/customer_limit_wizard_view.xml',
        'wizard/customer_delivery_wizard_view.xml',
        'views/partner_view.xml',
        'views/sale_order_view.xml',

    ],
    'demo': [],
    'css': [],
    'qweb': [],
    'js': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price':35,
    'currency':'EUR',
    'live_test_url':'https://youtu.be/CC-a6QQcxMc',
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
