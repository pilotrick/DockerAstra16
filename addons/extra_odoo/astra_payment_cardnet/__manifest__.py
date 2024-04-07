# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Astra Tech Cardnet',
    'version': '16.0.0.1',
    'category': 'Accounting/Payment Acquirers',
    'sequence': 380,
    'summary': 'Payment Acquirer: Cardnet Implementation',
    'description': """Cardnet Payment Acquirer""",
    'depends': ['payment'],
    'data': [
        'views/payment_views.xml',
        'views/payment_transations_views.xml',
        'views/payment_cardnet_templates.xml',
        'data/payment_provider_data.xml',
    ],
    'application': True,
    'uninstall_hook': 'uninstall_hook',

    'license': 'LGPL-3',
}
