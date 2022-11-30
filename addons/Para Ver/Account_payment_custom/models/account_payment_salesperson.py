from odoo import fields, models,_

class account_payment_salesperson(models.Model):
    _inherit ='account.payment'


    salesperson = fields.Many2one(string="Sales Person",related="partner_id.user_id")