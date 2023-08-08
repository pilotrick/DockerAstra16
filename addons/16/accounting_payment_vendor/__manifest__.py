# Copyright 2023 International Pack & Paper
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Payment Vendor',
    'version': '1.0.0',
    'category': 'Accounting',
    'summary': 'Adds a vendor column to payment tree view',
    'description': 'This module adds a vendor column to the tree view of payments in accounting.',
    'depends': ['account'],
    "website": "https://ippdr.com/",
    "author": "Astratech",
    "license": "AGPL-3",
    'data': [
        'views/account_payment_inherit.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
