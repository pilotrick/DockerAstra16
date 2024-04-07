# -*- coding: utf-8 -*-

from odoo import models, fields, api
from ast import literal_eval

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	send_cost_mail_alert = fields.Boolean("Send Cost Alert")
	partner_ids = fields.Many2many('res.partner', string="Users")

	@api.model
	def get_values(self):
		res = super(ResConfigSettings, self).get_values()
		get_param = self.env['ir.config_parameter'].sudo().get_param
		partner_ids = get_param('ld_product_cost_mail_alert.partner_ids', '[]')
		partner_ids = [(6, 0, literal_eval(partner_ids))]
		res.update(
			send_cost_mail_alert = self.env['ir.config_parameter'].sudo().get_param('ld_product_cost_mail_alert.send_cost_mail_alert'),
			partner_ids = partner_ids,
		)
		return res

	def set_values(self):
		res = super(ResConfigSettings, self).set_values()
		param = self.env['ir.config_parameter'].sudo()
		param.set_param('ld_product_cost_mail_alert.send_cost_mail_alert', self.send_cost_mail_alert)
		print("self.partner_ids.ids : ", self.partner_ids.ids)
		param.set_param('ld_product_cost_mail_alert.partner_ids', self.partner_ids.ids)
		return res

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	# send cost alert mail to users
	def action_confirm(self):
		res = super(SaleOrder, self).action_confirm()
		get_param = self.env['ir.config_parameter'].sudo().get_param
		p_list = []
		for line in self.order_line:
			if line.price_unit < line.product_id.standard_price:
				p_list.append(line.product_id.id)
		orderLines = self.order_line.filtered(lambda a:a.product_id.id in p_list)
		if orderLines:
			send_alert = get_param('ld_product_cost_mail_alert.send_cost_mail_alert')
			partner_ids = get_param('ld_product_cost_mail_alert.partner_ids', '[]')
			if send_alert and literal_eval(send_alert):
				partners = self.env['res.partner'].browse(literal_eval(partner_ids))
				self.env.context = dict(self.env.context)
				for partner in partners:
					names = [line.product_id.name for line in orderLines]
					self.env.context.update({
						'email_to': partner.email if partner.email else '',
						'user_name': partner.name,
						'order_items': ', '.join(names) if len(names) > 0 else ''})
					mail_template = self.env.ref('ld_product_cost_mail_alert.cost_mail_template_alertt')
					mail_template.with_context(email_to=partner.email,user_name=partner.name,order_items= ', '.join(names) if len(names) > 0 else '').sudo().send_mail(self.id, force_send=True,email_values={
                                                                                                        'email_to': partner.email})
		return res