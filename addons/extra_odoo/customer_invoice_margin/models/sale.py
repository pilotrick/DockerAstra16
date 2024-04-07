
# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo import tools
import datetime

class SaleOrderLine(models.Model):
	_inherit = "sale.order.line"

	def _prepare_invoice_line(self, **optional_values):
		res = super(SaleOrderLine, self)._prepare_invoice_line()
		res.update({'sale_id' : self.id})
		return res
