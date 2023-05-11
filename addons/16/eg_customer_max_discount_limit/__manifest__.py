{
    "name": "Customer Maximum Discount Limit",

    'version': "16.0",

    'category': "Set Limit",

    "summary": "This will set maximum discount limit for particular customer.",

    'author': "INKERP",

    'website': "https://www.INKERP.com",

    "depends": ['sale'],

    "data": [
        "views/res_partner_view.xml",
        "views/sale_order_view.xml",
    ],

    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
