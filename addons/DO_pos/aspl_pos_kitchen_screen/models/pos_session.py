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
from odoo import api, fields, models, _


class PosSession(models.Model):
    _inherit = 'pos.session'

    def load_pos_data(self):
        res = super(PosSession, self).load_pos_data()
        broad_cast_data = self.env['pos.order'].get_broadcast_data()
        res.update({'kitchen.data': broad_cast_data})
        res.update(
            {'delivery.users': self.env['res.users'].search_read([('kitchen_screen_user', '=', 'delivery')], ['name'])})
        return res

    def _pos_ui_models_to_load(self):
        result = super(PosSession, self)._pos_ui_models_to_load()
        if self.config_id.restaurant_mode:
            result.append('remove.product.reason')
            result.append('pos.order')
        if self.config_id.service_ids:
            result.append('delivery.type')
        return result

    def _loader_params_delivery_type(self):
        return {
            'search_params': {
                'domain': [('id', 'in', self.config_id.service_ids.ids)],
                'fields': ['name', 'delivery_type', 'charges', 'image', 'user_ids'],
            },
        }

    def _get_pos_ui_delivery_type(self, params):
        return self.env['delivery.type'].search_read(**params['search_params'])

    def _loader_params_remove_product_reason(self):
        return {'search_params': {'domain': [], 'fields': ['name', 'description']}}

    def _get_pos_ui_remove_product_reason(self, params):
        return self.env['remove.product.reason'].search_read(**params['search_params'])

    def _loader_params_pos_order(self):
        return {'search_params': {'domain': [('state', '=', 'draft')], 'fields': ['id']}}

    def _get_pos_ui_pos_order(self, params):
        return self.env['pos.order'].search_read(**params['search_params'])

    def _loader_params_res_users(self):
        result = super()._loader_params_res_users()
        result['search_params']['fields'].extend(
            ['kitchen_screen_user', 'pos_category_ids', 'is_delete_order_line', 'delete_order_line_reason'])
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
