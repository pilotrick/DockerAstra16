# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class sale_configuration_settings(models.TransientModel):
	_inherit = "res.config.settings"

	amount_range = fields.Float("Amount Range")

	def set_values(self):
		"""employee setting field values"""
		res = super(sale_configuration_settings, self).set_values()
		self.env['ir.config_parameter'].set_param('sales_amount_approval.amount_range',
												  self.amount_range)
		return res

	def get_values(self):
		"""employee limit getting field values"""
		res = super(sale_configuration_settings, self).get_values()
		value = self.env['ir.config_parameter'].sudo().get_param(
			'sales_amount_approval.amount_range')
		res.update({'amount_range':value})
		return res
