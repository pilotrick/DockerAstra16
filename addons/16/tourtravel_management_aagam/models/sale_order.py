from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_package = fields.Boolean(string="Is Package")
    arrival_date = fields.Date(string='Arrival Date')
    return_date = fields.Date(string='Departure Date')
    agent_id = fields.Many2one('res.partner', string='Agent')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    meals = fields.Char('Meals')
    time = fields.Char("Time")
    day_date = fields.Date('Date')
    days = fields.Char("Days")

