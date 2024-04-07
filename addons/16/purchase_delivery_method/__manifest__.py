# Copyright 2018-2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

{
    'name': "Purchase Delivery Method",
    'summary': """
        This module add delivery method in the purchase order and
        fill the value from the partner selected""",
    'version': "16.0.1.0.0",
    'category': 'Purchases',
    'website': "http://sodexis.com/",
    'author': "Sodexis",
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'depends': [
        'base',
        'delivery',
        'purchase',
    ],
    'images': ['images/main_screenshot.png'],
    'data': [
        'views/res_partner_view.xml',
        'views/purchase_view.xml',
    ],
}
