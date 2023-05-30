# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    it_salesperson = fields.Many2one("hr.employee", string="Salesperson")
