# -*- coding: utf-8 -*-
#################################################################################
# Author      : Ashish Hirpara (<www.ashish-hirpara.com>)
# Copyright(c): 2021
# All Rights Reserved.
#
# This module is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': 'Advanced Web Domain Widget',
    'version': '16.0.1.0.2',
    'summary': 'Set all relational fields domain by selecting its records unsing `in, not in` operator.',
    'sequence': 10,
    'author': 'Astratech',
    'license': 'OPL-1',
    'website': 'https://ashish-hirpara.com/r/odoo',
    'description':"""
      
        """,
    "price": "1.00",
    "currency": "USD",
    'depends': ['base', 'web'],
    'data':[
        # 'views/assets.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            "/advanced_web_domain_widget/static/src/xml/domain_base.xml"
        ],
        'web.assets_backend': [
            "advanced_web_domain_widget/static/src/core/**/*",
            "advanced_web_domain_widget/static/src/js/domain/**/*",
            "advanced_web_domain_widget/static/src/js/service/views_service.js",
            # "/advanced_web_domain_widget/static/src/js/fields16/basic_fields.js",
            # "/advanced_web_domain_widget/static/src/js/fields16/terabits_fields_registry.js",
            "/advanced_web_domain_widget/static/src/scss/style.scss",
            # "/advanced_web_domain_widget/static/src/js/widget16/domain_selector_dialog.js",
            # "/advanced_web_domain_widget/static/src/js/widget16/model_field_selector.js",
            # "/advanced_web_domain_widget/static/src/js/widget16/model_record_selector.js",
            # "/advanced_web_domain_widget/static/src/js/widget16/TerabitsDomainSelector.js",
        ],
    },
    'images': ['static/description/banner.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
}
