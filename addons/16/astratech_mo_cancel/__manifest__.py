{
    'name' : 'Cancel Manufacturing Order',
    'version' : '14.0.0.1',
    'website': 'https://astratech.com.do',
    'author': 'Astra Tech SRL',
    'category': 'Manufacturing',
    'maintainer': 'Jeffry J. De La Rosa',
   
    'summary': """Cancel manufacturings Order """,
    'license': 'OPL-1',
    'depends' : ['mrp','account'],
    'data': [
        'views/res_config_settings_views.xml',
	    'views/view_manufacturing_order.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,

}
