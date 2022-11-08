# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools,_


class res_user(models.Model):
    _inherit = 'res.users'

    sale_user_approver = fields.Many2one('res.users',string="User for Head of Sales")
