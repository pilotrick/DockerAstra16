# -*- coding: utf-8 -*-

{
    'name': 'POS Restaurant Sync Websocket Tensordoo',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'Tensordoo',
    'summary': 'Easy way to Sync Restaurant orders with Websocket',
    'description': """
=======================
Easy way to Sync Restaurant orders
""",
    'depends': ['pos_sync_order','pos_restaurant'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            "pos_sync_restaurant/static/src/js/pos.js",
            "pos_sync_restaurant/static/src/css/pos.css",
            'pos_sync_restaurant/static/src/xml/**/*',
        ],
    },
    'images': [
        'static/description/table_view.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 250,
    'currency': 'EUR',
}
