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
from odoo.http import Controller, route, request
from odoo.http import request


class KitchenScreenBackend(Controller):

    @route('/get_pos_order_data', type='json', auth='public')
    def get_pos_order_data(self):
        pos_user_categories = request.env['res.users'].sudo().search_read([('id', '=', request.env.context.get('uid'))],
                                                                          ['pos_category_ids'])
        return pos_user_categories[0].get('pos_category_ids')

    @route('/get_user_role', type='json', auth='public')
    def get_user_role(self):
        kitchen_user_role = request.env['res.users'].sudo().search_read([('id', '=', request.env.context.get('uid'))],
                                                                        ['kitchen_screen_user'])
        return kitchen_user_role[0].get('kitchen_screen_user')

    @route('/load_screen_data', type='json', auth='public')
    def load_screen_data(self):
        kitchen_data = request.env['pos.order'].sudo().with_context({'from_backend': True}).broadcast_order_data(False)
        return kitchen_data

    @route('/update_order_state', type='json', auth='public')
    def update_order_state(self, **kwargs):
        request.env['pos.order.line'].sudo().update_all_orderline_state(kwargs)

    @route('/update_orderline_state', type='json', auth='public')
    def update_order_line_state(self, **kwargs):
        request.env['pos.order.line'].sudo().update_orderline_state(kwargs)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
