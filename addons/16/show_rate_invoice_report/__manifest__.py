{
    'name': "Tasa En Factura",
    'summary': "Show USD rate in invoice report",
    'author': "Astra Tech SRL",
    'category': 'Hidden',
    'version': '14.0.0.1',
    'depends': [
        'account', 'l10n_do_accounting'
    ],
    # always loaded
    'data': [
        'views/report_invoice.xml',
    ],
    'installable': True,
}
