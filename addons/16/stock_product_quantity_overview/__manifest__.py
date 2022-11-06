# -*- coding: utf-8 -*-r
# Copyright (c) Open Value All Rights Reserved

{
    'name': 'Stock Product Quantity Overview',
    'summary': 'Stock product quantity overview',
    'version': '16.0.1.0',
    'category': 'Inventory',
    'website': 'www.openvalue.cloud',
    'author': "OpenValue",
    'support': 'info@openvalue.cloud',
    'license': "Other proprietary",
    'price': 0.00,
    'currency': 'EUR',
    'depends': [
        'stock',
    ],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_product_quantity_overview.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
}
