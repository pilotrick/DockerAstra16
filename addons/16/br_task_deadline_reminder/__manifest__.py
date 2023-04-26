

{
    'name': "Br Task Deadline Reminder",
    'version': '16.0.1.0.0',
    'author': 'Astratech',
    'company': 'Banibro IT Solutions Pvt Ltd.',
    'website': 'https://banibro.com',
    'summary': '''Task Deadline Reminder''',
    'description': '''Automatically Send Mail To Responsible User if Deadline Of Task is Today''',
    'category': "Project",
    'depends': ['project'],
    'license': 'AGPL-3',
    'email': "support@banibro.com",
    'data': [
            'views/deadline_reminder_view.xml',
            'views/deadline_reminder_cron.xml',
            'data/deadline_reminder_action_data.xml'
             ],
    'images': ['static/description/banner.png',
                'static/description/icon.png',],
    'installable': True,
    'auto_install': False
}
