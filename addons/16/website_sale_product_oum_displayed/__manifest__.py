# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Display product unit of measure in e-commerce",
    "version": "16.0.1.0.2",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    'author': 'Astratech',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ['base', 'website_sale'],
    "data": [
    "views/website_sale_views.xml",
    "views/product_template_form_inherit.xml",
    "security/ir.model.access.csv"
    ],
}
