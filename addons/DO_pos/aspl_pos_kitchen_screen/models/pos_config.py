# -*- coding: utf-8 -*-
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


class PosConfig(models.Model):
    _inherit = 'pos.config'

    restaurant_mode = fields.Selection([('full_service', 'Full Service Restaurant (FCS)'),
                                        ('quick_service', 'Fast-Food/Quick Service Restaurant (QSR)')],
                                       "Restaurant Mode", default="full_service")
    service_ids = fields.Many2many('delivery.type', string="Services")
    default_delivery_type = fields.Selection(
        [('take_away', 'Take Away'), ('dine_in', 'Dine In'), ('delivery', 'Delivery')],
        string="Default Delivery Type", default="take_away", help="Select Your Delivery Type")
    delivery_charge_product_id = fields.Many2one('product.product', string="Delivery Charge Product")

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.context.get('from_pos'):
            user_id = self.env['res.users'].browse([self.env.context.get('uid')])
            if user_id and user_id.kitchen_screen_user in ['waiter', 'cook']:
                args += [('id', '=', user_id.default_pos.id)]
        return super(PosConfig, self).search(args, offset=offset, limit=limit, order=order, count=count)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
