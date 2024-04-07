# -*- coding: utf-8 -*-

{
  'name': 'Website Access Restriction',
  'version': '1.0',
  'category': 'Website',
  'summary': 'Restringe el acceso a precios y carrito para usuarios no registrados.',
  'description': 'Este módulo extiende la funcionalidad del sitio web en Odoo para restringir a los usuarios no registrados de ver los precios y agregar productos al carrito.',
  'autor': 'International Pack & Paper',
  'website': 'https://www.ippdr.com',
  'depends': ['base', 'website_sale'],
  'assets': {
    'website.assets_wysiwyg': [
      ('include', 'web._assets_helpers'),
      # snippets
      'website_access_restriction/static/src/snippets/s_searchbar/options.js',
    ],
  },
  'data': [
    #views
    'views/website_sale_view.xml',
    'views/snippets/s_searchbar.xml'
  ],
  'instalable': True,
  'application': False,
  'auto_install': True,
  'licence': 'AGPL-3'
}