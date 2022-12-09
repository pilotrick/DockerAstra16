# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################
{
    'name': "Sales Approval",
    'category': 'Sales',
    'version': '1.1',
    'author': 'Equick ERP',
    'depends': ['base', 'sale','sale_management','sale_margin','dev_customer_credit_limit'],
    'website': "",
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sale_order_view.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: