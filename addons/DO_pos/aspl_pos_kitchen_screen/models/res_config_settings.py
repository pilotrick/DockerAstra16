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

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_restaurant_mode = fields.Selection(related='pos_config_id.restaurant_mode',
                                           readonly=False, string='Restaurant Mode')
    pos_service_ids = fields.Many2many(related='pos_config_id.service_ids', readonly=False, string='Services')
    pos_default_delivery_type = fields.Selection(related='pos_config_id.default_delivery_type', readonly=False,
                                                 string='Select Default Delivery Type')
    pos_delivery_charge_product_id = fields.Many2one(related='pos_config_id.delivery_charge_product_id', readonly=False,
                                                     string='Delivery Charge Product')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
