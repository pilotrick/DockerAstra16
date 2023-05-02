# Copyright 2023 International Pack & Paper
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale Order Customer Invoice',
    'version': '1.0.0',
    'category': 'Sales',
    'summary': 'Adds a tab in the sale order view to see the invoices not paid of the selected customer.',
    'description': 'Adds a tab in the sale order view to see the invoices not paid of the selected customer.',
    'depends': ['sale'],
    'author': 'International Pack & Paper',
    'website': 'https://ippdr.com/',
    'license': 'AGPL-3',
    'data': [
      'views/sale_order_view.xml',
      'security/ir.model.access.csv'
    ],
    'installable': True,
    'auto_install': False,
    'application': False
}