# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Website Sale Product UOM Displayed",
    "version": "16.0.1.0.2",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ['base', 'website_sale'],
    "data": [
    "data/snippet_filter_data.xml",
    "views/website_sale_views.xml",
    "views/product_template_form_inherit.xml",
    "security/ir.model.access.csv"
    ],
}
