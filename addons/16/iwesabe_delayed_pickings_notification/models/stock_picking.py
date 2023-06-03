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

from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from odoo.http import Controller, request, route


class Picking(models.Model):
	_inherit = 'stock.picking'

	def send_mail_picking_in_date_deadline_crossed(self):
		for picking in self.search([('picking_type_id.code', '=', 'incoming'),('state', 'not in', ['done', 'cancel'])]):
			po = self.env['purchase.order'].search([('name', '=', picking.origin)])
			email_list = [order.user_id.partner_id.email for order in po if order.user_id.partner_id.email]
			if not picking.user_id.partner_id.email or not picking.date_deadline:
				continue
			email_list.append(picking.user_id.partner_id.email)
			if picking.date_deadline.date() < date.today():
				base_url = request.env['ir.config_parameter'].get_param('web.base.url')
				base_url += '/web#id=%d&view_type=form&model=%s' % (picking.id, picking._name)
				template = """
					<body style="font-family:sans-serif;line-height:2;">
					Hello Dear,<br/>
					Date Deadline crossed for this picking please validate {picking_name}.<br/>
					Thanks.<br/>
					<br/>
					<a href="{base_url}"
							style="background:#86597b;color:white;padding:12px;text-decoration:none;border-radius:6px;">
							Validate
					</a>
					<br/>
					<br/>
					<hr/>
					</body>
					""".format(base_url=base_url, picking_name=picking.name,)

				template_id = self.env.ref(
					'iwesabe_delayed_pickings_notification.email_template_picking_in_deadline_crossed_reminder').id
				if template_id:
					email_template_obj = self.env['mail.template'].browse(template_id)
					email_values = {
						'email_to': ','.join(email_list),
						'body_html': template
					}
					email_template_obj.send_mail(picking.id, force_send=True, email_values=email_values)
		return True