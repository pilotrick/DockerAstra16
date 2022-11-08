# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class stock_warehouse(models.Model):
    _inherit = "stock.warehouse"

    display_stock_webshop = fields.Boolean(string="Display Stock on Website")