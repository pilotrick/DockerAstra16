# -*- coding:utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Uncannycs LLP
#    Copyright (C) 2022 Uncannycs LLP (<http://uncannycs.com>).
#
##############################################################################

{
    "name": "Separate Customer Vendor ",
    "summary": """Separate Customer Vendor """,
    "version": "16.0.0.0.0",
    "author": "Astratech",
    'maintainer': 'Uncanny Consulting Services LLP',
    'website': 'http://www.uncannycs.com',
    "license": "AGPL-3",
    "installable": True,
    "depends": ['sale_management', 'purchase'],
    "data": [
        'views/sale_purchase.xml'
    ],
    'images': ['static/description/banner.gif'],
}
