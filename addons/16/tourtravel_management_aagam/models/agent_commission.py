# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AgentCommissionLine(models.Model):
    _name = 'agent.commission.line'
    
    name = fields.Char(string='Name')
    partner_id = fields.Many2one('res.partner', string='Customer')
    booking_information_id = fields.Many2one('booking.information', string='Booking Information ID')
    commission = fields.Float(string='Commission')
    cost = fields.Float(string='Cost')
    agent_commission_id = fields.Many2one('agent.commission', string='Agent Commission')
    

class AgentCommission(models.Model):
    _name = 'agent.commission'
    _description = 'Agent Commission'
    
    name = fields.Char(string='Name')
    partner_id = fields.Many2one('res.partner', string='Agent')
    date = fields.Date(string='Date', tracking=True)
    pricelist_id = fields.Many2one('res.currency', string='Pricelist')
    commission_line_ids = fields.One2many('agent.commission.line', 'agent_commission_id', string='Commission Line')
    
    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('agent.commission.seq') or '/'
        return super(AgentCommission, self).create(values)
        