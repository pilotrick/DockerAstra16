# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################
{
    'name': "Customer Pricelist",
    'category': 'Sales',
    'version': '1.0',
    'author': 'Equick ERP',
    'description': """
        Allow user to create the pricelist from contact
    """,
    'summary': 'Allow user to create the pricelist from contact',
    'depends': ['base', 'sale_management'],
    'website': "",
    'data': ['security/ir.model.access.csv',
             'views/partner_view.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: