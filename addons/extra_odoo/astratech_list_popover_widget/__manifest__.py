# flake8: noqa: E501
{
    "name": "AstraTech List Popover Widget",
    "version": "16.0.0.0.1",
    "author": "Jeffry J. De La Rosa",
    "website": "https://astratech.com.do",
    'summary': 'Tooltips message for text fields on tree view.',
    "license": "LGPL-3",
    'category': 'Technical Settings',
    'depends': [
        'web',
    ],
    'assets': {
        'web.assets_qweb': [
            'astratech_list_popover_widget/static/src/xml/popover_templates.xml',
        ],
        'web.assets_backend': [
            'astratech_list_popover_widget/static/src/css/list_popover_widget.css',

            'astratech_list_popover_widget/static/src/js/list_popover_mixin.js',
            'astratech_list_popover_widget/static/src/js/list_text_popover_widget.js',
            'astratech_list_popover_widget/static/src/js/list_char_popover_widget.js',
            'astratech_list_popover_widget/static/src/js/list_html_popover_widget.js',
        ],
    },
    'images': [],
    'installable': True,
    'auto_install': False,
}
