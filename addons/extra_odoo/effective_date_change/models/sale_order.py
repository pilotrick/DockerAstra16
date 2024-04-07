# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"


    def _prepare_confirmation_values(self):
        
       
        if not self.date_order:
            return {
                'state': 'sale',
                'date_order': fields.Datetime.now()
            }
        else:
            return {
                'state': 'sale',
            }