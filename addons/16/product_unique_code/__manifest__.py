# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Unique Product Internal Reference",
    "summary": "Set Product Internal Reference as Unique",
    
    "version": "15.0.0.0.1",
    "license": "AGPL-3",
    
    "author": "Astratech",
    "website": "https://fr.fiverr.com/kamelbenchehida",

    "category": "Product",
    "sequence": 1,
    
    "depends": ["product", "stock"],
    "data": {
        "wizards/product_default_code.xml",
        "security/ir.model.access.csv"
    },

    "installable": True,
    "application": True,
    "auto_install": False,
}
