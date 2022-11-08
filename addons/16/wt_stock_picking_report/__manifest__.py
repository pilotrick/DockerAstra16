# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    "name": "wt stock picking receipt",
    "version": "14.0.1.0",
    "category": "stock",
    "summary": "wt stock picking receipt",
    "description": """
    stock picking receipt.
    """,
    "website": "http://warlocktechnologies.com",
    "author": "Astratech",
    "support": "info@warlocktechnologies.com",
    "depends": ["stock"],
    "data": [
        'reports/picking_report.xml',
        'reports/picking_report_template.xml',
        'views/stock_picking_view_inherite.xml',
    ],
    "images": ["images/screen_image.png"],
    "installable": True,
}
