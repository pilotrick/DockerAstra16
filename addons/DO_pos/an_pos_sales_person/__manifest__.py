# -*- coding: utf-8 -*-
{
    "name": "POS Salesperson",
    "category": "Point of Sale",
    'version': '16.0.1.0.0',
    "summary": "This module will help to user set salesperson name on POS Order line from "
               "POS Screen also can get salesperson in POS Receipt",
    "description": "This module will help to user set salesperson name on POS Order line from "
                   "POS Screen also can get salesperson in POS Receipt",
    "license": "LGPL-3",
    'author': "Adel Networks S.R.L",
    "depends": ["l10n_do_pos", "pos_hr"],
    "data": [
        "security/res_groups.xml",
        "views/views.xml",
        "views/pos_config_view.xml",
        "views/pos_order_report_view.xml",
    ],
    "assets": {
        "point_of_sale.assets": [
            "an_pos_sales_person/static/src/css/pos.css",
            "an_pos_sales_person/static/src/js/pos.js",
            "an_pos_sales_person/static/src/js/TicketScreen/TicketScreen.js",
            "an_pos_sales_person/static/src/js/ProductScreen/ProductScreen.js",
            "an_pos_sales_person/static/src/js/HeaderButton.js",
            "an_pos_sales_person/static/src/js/HeaderLockButton.js",
            "an_pos_sales_person/static/src/xml/pos.xml",
        ],
    },
}
