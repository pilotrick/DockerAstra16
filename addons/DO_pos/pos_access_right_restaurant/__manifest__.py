# -*- coding: utf-8 -*-
{
    "name": "Extra Access Right Restaurant",
    "version": "15.0.1.2",
    "summary": "Extra Access Right for certain actions",
    "license": "AGPL-3",
    "depends": ["pos_restaurant"],
    "data": [
        "security/res_groups.xml",
    ],
    'assets': {
            'point_of_sale.assets': [
                'pos_access_right_restaurant/static/src/js/**/*',
                'pos_access_right_restaurant/static/src/css/pos.css',
                'pos_access_right_restaurant/static/src/xml/**/*',
            ],
        },
}
