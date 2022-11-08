# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Whatsapp',
    'version': '16.0.1.0.0',
    'sequence': 10,
    'category': 'Extra Tools',
    'summary': """
        Whatsapp Redirect
    """,
    'description': "Whatsapp Redirect",
    "author": "Astratech",
    'maintainer': 'Dx Deace',
    'website': '',
    'license': 'LGPL-3',
    'images': [
        'static/description/ss.png'
    ],
    'depends': [
        'base',
        'web',
        'mail'
    ],
    'data': [
    ],
    'assets': {
        'mail.assets_discuss_public': [
            'dx_whatsapp/static/src/components/wa_button/*',
        ],
        'web.assets_backend': [
            'dx_whatsapp/static/src/components/*/*',
        ],
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
}
