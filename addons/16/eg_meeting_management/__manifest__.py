{
    'name': 'Meeting Minutes',
    'version': '16.0.1.0.0',
    'category': 'Productivity/Calendar',
    'summary': 'Manage Minute Meeting in Calender',
    'author': 'INKERP',
    'website': 'https://www.INKERP.com/',
    'depends': ['calendar'],
    
    'data': [
        'security/ir.model.access.csv',
        'views/minute_meeting_view.xml',
    ],
    
    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
