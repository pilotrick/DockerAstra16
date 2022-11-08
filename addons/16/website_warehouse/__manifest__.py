{
    'name': 'Website Warehouse',
    'category': 'Website',
    'sequence': 55,
    'summary': 'Select warehouse in checkout page',
    'website': '',
    'version': '1.1',
    'description': "",
    'depends': ['payment', 'web', 'website_sale', 'stock'],
    'data': [
        'views/payment_template.xml',
        'views/stock_warehouse.xml',
        'data/warehouse.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'website_warehouse/static/src/js/payment_form.js',
        ]
    },

    
}
