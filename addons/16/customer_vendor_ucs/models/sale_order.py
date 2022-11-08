# -*- coding:utf-8 -*-
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_id = fields.Many2one(
        'res.partner',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('customer_rank', '>', 0)]",)