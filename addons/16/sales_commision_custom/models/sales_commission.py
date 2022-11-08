# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools,_


class SALESCOMMISSION(models.Model):
    _inherit = 'sale.commission'

    # days_1 = fields.Integer("From Days")
    # days_2 = fields.Integer("To Days")
    # das_from = fields.Selection(selection=[('1to30',"1 to 30"),
    #                              ('31to60',"31 to 60"),
    #                              ('61to90'),("61 to 90")
    #                              ],string="Days From",default='1to30')
    das_from = fields.Selection([
        ('1to30', '1 to 30'),('31to60', '31 to 60'),('61to90', '61 to 90'),], default=False,string="Days From")