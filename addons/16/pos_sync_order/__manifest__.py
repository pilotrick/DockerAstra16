# -*- coding: utf-8 -*-

{
    'name': 'POS Order Sync',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'Webveer',
    'summary': 'We can easily sync orders to different sessions.',
    'description': """

=======================

""",
    'depends': ['point_of_sale','pos_longpolling'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/templates.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            "pos_sync_order/static/src/js/pos.js",
            "pos_sync_order/static/src/css/pos.css",
        ],
        'web.assets_qweb': [
            'pos_sync_order/static/src/xml/**/*',
        ],
    },
    'images': [
        'static/description/auto.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 120,
    'currency': 'EUR',
}
