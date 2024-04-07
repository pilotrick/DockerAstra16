{
    'name': "Product price currency",
    'summary': "Product price USD currency convertion",
    'author': "Astratech",
    'category': 'Warehouse',
    'version': '16.0.0.1',
    'depends': [
        'product',
        'account',
    ],
    'license': 'AGPL-3',
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/cron_job.xml',
        'views/product_views.xml',
    ],
    'installable': True,
}
