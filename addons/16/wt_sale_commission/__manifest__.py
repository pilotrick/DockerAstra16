# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    "name": "Sales commission",
    "version": "1.2",
    "category": "sale",
    "summary": "Sales Commission customization.",
    "description": """
        user get the commission based on their payment period.
    """,
    "author": "Astratech",
    "website": "http://warlocktechnologies.com",
    "support": "info@warlocktechnologies.com",
    "depends": ["base", "sale", "customer_invoice_margin"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/account_move_view.xml",
        "views/res_users_view.xml",
        "views/sale_commission_view.xml",
    ],
    "images": [],
    "license": "OPL-1",
    "installable": True,
}
