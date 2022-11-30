# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import datetime

class AccountMove(models.Model):
    _inherit = "account.move"
    
    payment_dates = fields.Char(string='Payment Dates', compute="compute_payment_dates")
    
    def compute_payment_dates(self):
        for rec in self:
            rec.payment_dates = ''
            payment_id = rec._get_reconciled_payments()
            payments = self.env['account.payment'].search([('id','in',payment_id.ids)])
            for payment in payments:
                payment_date = payment.date
                if payment_date:
                    if rec.payment_dates == '':
                        rec.payment_dates += payment_date.strftime('%d/%m/%Y')
                    else:
                        rec.payment_dates += ', ' + payment_date.strftime('%d/%m/%Y')
                        
                        
                        