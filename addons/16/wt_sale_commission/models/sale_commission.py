# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleCommission(models.Model):
    _name = "sale.commission"
    _description = "Sale Commission"

    name = fields.Char("Name", required=True)
    based_on = fields.Selection([('amount', 'Amount'), ('margin', 'Margin')], required=True, default='amount')
    commission_line_ids = fields.One2many(
        "sale.commission.line", "commission_id", string="Commission Period"
    )
    minimum_margin_percent = fields.Float(string='Minimum Margin(%)')


class SaleCommissionLine(models.Model):
    _name = "sale.commission.line"
    _description = "Sale Commission Line"

    commission_id = fields.Many2one("sale.commission", "Commission", required=True)
    period_from = fields.Integer("Period From")
    period_to = fields.Integer("Period To")
    commission = fields.Float("Commission(%)")
