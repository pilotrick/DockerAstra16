# -*- coding: utf-8 -*-
from odoo import fields, api, models, _

class stock_pallet(models.Model):
	_inherit = "product.template"

	pallet_size = fields.Char(string="BULROS X PALETA")