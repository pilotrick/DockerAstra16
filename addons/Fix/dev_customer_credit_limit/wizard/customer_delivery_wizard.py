# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import api, fields, models , _
from datetime import datetime


class customer_delivery_wizard(models.TransientModel):
    _name = "customer.delivery.wizard"
    _description = 'Customer Delivery Wizard'

    message = fields.Char()
    users_ids = fields.Many2many('res.users','users_delivery_wizard_rel','delivery_id','user_id','Users')

    def action_create_activity(self):
        for record in self:
            delivery_id = self.env['stock.picking'].browse(self._context.get('active_id'))
            model_id = self.env.ref('dev_customer_credit_limit.model_stock_picking')
            type_id = self.env.ref('mail.mail_activity_data_todo')
            summary = record.message
            users = record.users_ids
            for user in users:
                activity_data = {
                    'res_id': delivery_id.id,
                    'res_model_id': model_id.id,
                    'activity_type_id': type_id.id,
                    'summary': summary,
                    'user_id': user.id,
                }
                self.env['mail.activity'].sudo().create(activity_data)
