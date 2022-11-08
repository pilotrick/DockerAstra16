# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    "name": "website product price hide for public user",
    "version": "1.0",
    "category": "website",
    "summary": "website ",
    "description": """
        webiste product price hide for public user, if they want to know the product price they can ask to support through click on "Ask Price" button.
    """,
    "author": "Astratech",
    "website": "http://warlocktechnologies.com",
    "support": "info@warlocktechnologies.com",
    "depends": ['website', 'website_sale', 'website_sale_wishlist','website_form',],
    "data": [
        "views/templates.xml",
        "views/website.xml",
        "views/cart_template.xml",
    ],

    "images": [],
    "license": "OPL-1",
    "installable": True,
    "qweb": [
            "static/src/xml/recently_viewd_product_template.xml",
        ],
}
