{
    'name': "Product cost currency",
    'summary': "Product cost USD currency convertion",
    'author': "Jeffry J. De La Rosa",
    'category': 'Warehouse',
    'version': '13.0.0.1',
    'depends': [
        'product',
        'account',
    ],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/cron_job.xml',
        'views/product_views.xml',
    ],
    'installable': True,
}
