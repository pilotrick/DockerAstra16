# -*- coding: utf-8 -*-

{
    'name': 'POS Order Sync Websocket',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'Tensordoo',
    'summary': 'We can easily sync orders to different sessions.With Websocket',
    'description': """

=======================

""",
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/templates.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            "pos_sync_order/static/src/js/pos.js",
            "pos_sync_order/static/src/css/pos.css",
            'pos_sync_order/static/src/xml/**/*',
        ],
    },
    'images': [
        'static/description/auto.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 250,
    'currency': 'EUR',
}
