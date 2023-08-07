# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Forcasting Report",
    "version": "14.0.1.0",
    "category": "sale",
    "summary": "Forcasting Report",
    "description": """
        Forcasting Report
    """,
    "author": "Silver Touch Technologies Limited",
    "website": "",
    "support": "",
    "depends": ["base", "sale", "purchase"],
    "data": [
        # DATA
        "data/forcasting_cron.xml",

        # SECURITY
        "security/ir.model.access.csv",

        # VIEWS
        "views/sale_forcasting_report_view.xml",
        "views/purchase_forcasting_report.xml",
        "views/menus.xml"
    ],
    "price": 0,
    "currency": "USD",
    "license": "OPL-1",
    "installable": True,
}
