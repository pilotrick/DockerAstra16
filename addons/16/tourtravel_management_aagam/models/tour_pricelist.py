# -*- coding: utf-8 -*-

from odoo import models, fields, _, api

class TourPricelist(models.Model):
    _name = "tour.pricelist"
    _description = "Pricelist"
    _inherit = "mail.thread"

    name = fields.Char(string="Name",required=1)
    room_type_id = fields.Many2one("room.type",string="Room Type")
    meal_plan_id = fields.Many2one("tour.meal.plan",string="Meal Plan")
    cancelation_id = fields.Many2one("tour.cancellation",string="Cancel Policy")
    adult = fields.Integer(string="Adult")
    kids = fields.Integer(string="Kids")
    date = fields.Date(string="Date")
    price = fields.Float(string="Price",force_save=1)

    @api.onchange("date")
    def _onchange_date_data(self):
        date_data_id = self.env['date.pricelist.data'].search([('date_list','=',self.date),('pricelist_id','=',self.name)])
        if date_data_id:
            self.price = date_data_id.price
        # else:
        #     self.price = 0.0

class DatePricelistData(models.Model):
    _name = "date.pricelist.data"
    _description = "Date Wise Price"
    _inherit = "mail.thread"

    pricelist_id = fields.Many2one("tour.pricelist",string="Pricelist")
    date_list = fields.Date(string="Tour")
    price = fields.Float(string="Price")