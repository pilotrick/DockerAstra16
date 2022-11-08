# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderGroup(models.Model):

    _inherit = "sale.order"

    button_group = fields.Boolean("Display",default=False)
    button_group_char = fields.Char("Compute",compute="compute_days")

    @api.depends('payment_term_id')
    def compute_days(self):
        for rec in self:
            if rec.user_has_groups('xs_sales_group.group_cf_user'):
                if self.payment_term_id.line_ids.days == 0:
                    rec.button_group = True #hide button
                else:
                    rec.button_group = False  # hide button
            else:
                rec.button_group = False
            rec.button_group_char = "Tick"
            pass