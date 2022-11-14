# Copyright 2018, 2021 Heliconia Solutions Pvt Ltd (https://heliconia.io)

{
    "name": "Sale Order History",
    "summary": """
        Odoo 14.0 Sales Order History
    """,
    "description": """
        Select Confirmed Sale Order(s) from history of particular
         customer and add into the new order.
    """,
    "author": "AstraTech",
    "website": "https://heliconia.io",
    "category": "Tools",
    "version": "15.0.0.1.0",
    "depends": ["sale_management"],
    "license": "OPL-1",
    # 'price': 19.00,
    "currency": "EUR",
    "data": [
        "security/ir.model.access.csv",
        "wizards/sale_order_history_wizard.xml",
        "views/sale.xml",
    ],
    # 'images': ['static/description/heliconia_sale_order_history.gif'],
}
