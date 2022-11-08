# -*- coding: utf-8 -*-

import json
from odoo import api, fields, models, _
from datetime import datetime


class ResUsers(models.Model):
    _inherit = "res.users"

    commission_id = fields.Many2one("sale.commission", string="Commission")
    user_commission_line_ids = fields.One2many(
        "user.commission.line", "user_id", string="User Commission"
    )

    def _get_commission_lines(self):
        result = []
        for invoice in self.env["account.move"].search(
            ['|', ("payment_state", "=", "paid"), ("payment_state", "=", "in_payment"), ("invoice_user_id", "=", self.id), ("move_type", '!=', 'out_refund')]
        ):

            date_lis = []
            
            payment_dict = json.loads(invoice.invoice_payments_widget)
            if payment_dict.get("content"):
                for payment in payment_dict["content"]:
                    date_lis.append(payment["date"])
            last_payment_date = max(date_lis)
            difference = fields.Date.from_string(last_payment_date) - (
                invoice.invoice_date
            )
            diff_days = difference.days
            

            commission_line = self.commission_id.commission_line_ids.filtered(
                lambda c: c.period_from <= diff_days
                and ((c.period_to >= diff_days) if c.period_to > 0 else True)
            )

            tmp = 1

            if commission_line:
                commission_perc = commission_line[0].commission
            else:
                commission_perc = 0
                tmp = 0
            
            commission_amount = 0.0
            flag = 1

            if commission_perc:
                
                invoice_credit_note = invoice.search([('credit_note_id', '=', invoice.id)])
                
                if invoice_credit_note:
                    if invoice_credit_note.payment_state == 'paid':
                        if invoice.amount_untaxed != invoice_credit_note.amount_untaxed and float(invoice.margin_amount) != float(invoice_credit_note.margin_amount): 
                            invoice = invoice_credit_note

                if (float(invoice.margin_percentage.replace("%",""))*100) >= self.commission_id.minimum_margin_percent:
                    if self.commission_id.based_on == 'amount':
                        commission_amount = (invoice.amount_untaxed * commission_perc) / 100
                    else:                                            
                        commission_amount = (float(invoice.margin_amount) * commission_perc) / 100
                else:
                    flag = 0
                
                if invoice.currency_id != invoice.company_id.currency_id:
                    currency_id = self.env['res.currency'].search([('id', '=', invoice.currency_id.id)])
                    rate = currency_id.rate_ids.filtered(lambda x:x.name ==  datetime.strptime(last_payment_date, '%Y-%m-%d').date() and x.company_id.id == invoice.company_id.id)
                    if rate:
                        commission_amount = commission_amount/rate.rate

            if flag and tmp:
                result.append(
                    (   
                        0,
                        0,
                        {
                            "customer_name":invoice.partner_id.name,
                            "move_id": invoice.id,
                            "move_amount": invoice.amount_untaxed,
                            "move_create_date": invoice.invoice_date,
                            "move_payment_date": fields.Date.from_string(
                                last_payment_date
                            ),
                            "commission_amount": commission_amount,
                            "commission_perc": commission_perc,
                            "payment_interval": int(diff_days),
                            "paid_amount": invoice.amount_total,
                            "tax_amount": invoice.amount_tax,
                            "margin_amount":float(invoice.margin_amount),
                            "margin_percentage":float(invoice.margin_percentage.replace("%",""))
                        },
                    )
                )
        return result

    def generate_commission_lines_cron(self):
        for record in self.search([('commission_id', '!=', False), ('commission_id.commission_line_ids', '!=', False)]):
            record.generate_commission_lines()

    def generate_commission_lines(self):
        self.ensure_one()
        if self.commission_id and self.commission_id.commission_line_ids:
            self.user_commission_line_ids.unlink()
            self.user_commission_line_ids = self._get_commission_lines()
        return True


class UserCommissionLine(models.Model):
    _name = "user.commission.line"
    _description = "User Commission Line"

    customer_name = fields.Char('Customer') 
    user_id = fields.Many2one("res.users", "Commission", required=True)
    move_id = fields.Many2one("account.move", "Invoice", required=True)
    move_amount = fields.Float("Untaxed Total Amount")
    move_payment_date = fields.Date("Payment Date")
    move_create_date = fields.Date("Invoice Date")
    commission_amount = fields.Float("Commission Amount")
    commission_perc = fields.Float("Commission(%)")
    payment_interval = fields.Integer("Payment Interval")
    paid_amount = fields.Float("Paid Amount")
    tax_amount = fields.Float("Tax Amount")
    margin_amount = fields.Float("Margin")
    margin_percentage = fields.Float("Margin(%)")