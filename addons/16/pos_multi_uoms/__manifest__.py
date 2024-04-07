# -*- coding: utf-8 -*-

{
    'name': 'Pos multi UOM',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'Astratech',
    'summary': 'Pos multi UOM allows you to sell one products in different unit of measure.',
    'description': "Pos multi UOM allows you to sell one products in different unit of measure.",
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_multi_uoms/static/src/js/pos.js',
            'pos_multi_uoms/static/src/xml/**/*',
        ],
    },
    'images': [
        'static/description/banner.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 29,
    'currency': 'EUR',
}
