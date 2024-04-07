# -*- coding: utf-8 -*-
{
    'name': "Reporte de venta",
    "description": """Reporte para gestionar las ventas realizadas""",
    "summary": "Reporte para gestionar las ventas realizadas",
    "category": "Accounting",
    "version": "16.0.1.0.0",
    'author': 'Astratech',
    'depends': ['account','customer_invoice_margin','warehouse_sales','sale'],
    'data': [
        'views/account_move_line_view.xml',
        'views/sale_order_view.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
