{
    'name': 'Receipt Status on Purchase order',
    'version': '16.0',
    'category': 'Sale',
    'summery': 'Receipt Status on Purchase order',
    'author': 'INKERP',
    'website': "https://www.INKERP.com",
    'depends': ['purchase', 'purchase_stock'],

    'data': [
        'views/purchase_order_view.xml',
    ],

    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
