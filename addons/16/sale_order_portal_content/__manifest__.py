# Copyright 2023 International Pack & Paper
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sales Order Portal Content",
    "version": "1.0.0",
    "category": "Sale",
    "website": "https://ippdr.com/",
    "author": "International Pack & Paper",
    "summary": "Add image and description to the sale order portal content view",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ['sale', 'portal'],
    "data": [
        "views/sale_order_portal_content.xml"
        ],
}
