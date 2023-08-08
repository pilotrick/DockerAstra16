{
    'name': 'Notificación de límite de crédito',
    'version': '1.0',
    'summary': 'Envía una notificación por correo electrónico cuando los pedidos alcanzan el estado de límite de crédito',
    'description': 'Este módulo crea una acción automatizada en el módulo de ventas para enviar un correo electrónico cuando los pedidos pasan al estado "credit_limit".',
    'category': 'Sales',
    'author': 'Astratech',
    'website': 'https://www.ippdr.com',
    'depends': [
      'base',
      'sale',
    ],
    'data': [
      #'data/data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
