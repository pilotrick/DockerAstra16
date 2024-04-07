# -- coding: utf-8 --
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
from odoo import models, fields, api


class DeliveryType(models.Model):
    _name = 'delivery.type'
    _description = 'Delivery Type Info'

    name = fields.Char(string="Name")
    delivery_type = fields.Selection([('take_away', 'Take Away'), ('dine_in', 'Dine In'), ('delivery', 'Delivery')],
                                     string='Order Type')
    charges = fields.Float(string="Charges")
    image = fields.Binary(string="Delivery Image")
    user_ids = fields.Many2many('res.users', string="User", domain=[('kitchen_screen_user', '=', 'delivery')])
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
