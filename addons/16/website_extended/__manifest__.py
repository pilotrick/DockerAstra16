{
    # Theme information
    'name': 'Webshop - Portal Extended',

    'version' : '15.0.0.1',
    'website': 'https://astratech.com.do',
    'author': 'Astra Tech SRL',
    'category': 'Website',
    'description': """""",
    'license': 'AGPL-3',
    
    # Dependencies
    'depends': [
        'website_sale_stock'
    ],

    # Views
    'data': [
        'templates/template.xml',
        'views/stock_warehouse_view.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            'website_extended/static/src/scss/website_extended.scss',
        ]

    },

    # Technical
    'installable': True,
    'application': True,
    
}
