# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    vehicle = fields.Many2one('fleet.vehicle', domain=[('picking_ok','=',True)])
    driver = fields.Many2one('res.partner')
    
    @api.onchange('vehicle')
    def set_driver(self):
        if self.vehicle and self.vehicle.driver_id:
            self.driver = self.vehicle.driver_id
        else:
            self.driver = False

class StockMove(models.Model):
    _inherit = 'stock.move'
    vehicle = fields.Many2one('fleet.vehicle', related='picking_id.vehicle', store=True, readonly=True)
    driver = fields.Many2one('res.partner', related='picking_id.driver', store=True, readolny=True)
    provider = fields.Many2one('res.partner')
    flag = fields.Boolean(compute = 'set_provider')

    @api.depends('flag')
    def set_provider(self):
        for stock_move in self:
            stock_move.flag = True
            stock_move.provider = stock_move.picking_id.partner_id

