{
    'name': 'Invoice total due',
    'version': '15.0.1.0',
    'summery': 'Add total due to customer invoices',
    'description': '''
        Add total due to customer invoices
    ''',
    'author': 'Astratech',
    'website': 'https://kareemabuzaid.com',
    'depends': [
        'account',
    ],
    'data': [
        'views/report_invoice.xml',
    ],
    'images': ['static/description/invoice.png'],
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
}
