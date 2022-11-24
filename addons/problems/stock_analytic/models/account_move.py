# -*- coding: utf-8 -*-
from numpy import require
from odoo import fields, models

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
        index=True, compute="_compute_analytic_account_id", store=True, readonly=False, require=True, check_company=True, copy=True)