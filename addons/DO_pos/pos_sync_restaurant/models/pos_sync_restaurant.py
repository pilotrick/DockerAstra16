# -*- coding: utf-8 -*-

from odoo import fields, models,tools,api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # def _get_floors_domain(self):
    #     print("Testing the floor>>>>>>>>>>>>>>>",self.pos_config_id.floor_ids.ids)
    #     return [('id', 'in', self.pos_config_id.floor_ids.ids)]

    pos_floor_ids = fields.Many2many(related='pos_config_id.floor_ids', readonly=False)

class pos_config(models.Model):
    _inherit = 'pos.config' 

    floor_ids = fields.Many2many(comodel_name='restaurant.floor',relation='restaurant_floor_config',column1='restaurant_floor_id',column2='config_id')

class restaurant_floor(models.Model):
    _inherit = 'restaurant.floor' 
    
    pos_config_id2 = fields.Many2many(comodel_name='pos.config',relation='restaurant_floor_config',column1='config_id',column2='restaurant_floor_id')


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_restaurant_floor(self):
        result = super()._loader_params_restaurant_floor()
        result['search_params']['domain'] = [('id', 'in', self.config_id.floor_ids.ids)];
        return result