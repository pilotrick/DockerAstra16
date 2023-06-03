# -*- coding: utf-8 -*-
##############################################################################
#
#    Global Creative Concepts Tech Co Ltd.
#    Copyright (C) 2018-TODAY iWesabe (<http://www.iwesabe.com>).
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Delayed Pickings Notification',
    'version': '15.0.0.0',
    'author': 'iWesabe',
    'summary': 'Email notification for delayed incoming pickings',
    'description': """This module helps to send the mail notification to 
                    purchase representative and picking responsible user for delayed incoming pickings.""",
    'category': 'Inventory/Inventory',
    'website': 'https://www.iwesabe.com/',
    'license': 'LGPL-3',
    'depends': ['purchase','stock'],
    'data': [
        'data/ir_cron_data.xml',
        'data/mail_data.xml',
    ],
    'qweb': [],
    'images': ['static/description/iWesabe-Apps-delayed-pickings-notify.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
