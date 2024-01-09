# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class RoomTypeInformation(models.Model):
    _name = 'room.type.information'
    _description = 'Room Type Information'
    
    name = fields.Char(string='Name')
    room_type_id = fields.Many2one('room.type', string='Room Type')
    cost_price = fields.Float(string='Cost Price')
    sale_price = fields.Float(string='Sale Price')
    description = fields.Char(string='Description')
    room_type_info_id = fields.Many2one('accomodation.information', string='Room Type')


class AccomodationInformation(models.Model):
    _name = 'accomodation.information'
    _description = 'Hotel Reservation'
    
    name = fields.Char(string='Name')
    room_type_id = fields.Many2one('room.type', string='Room Type')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    partner_id = fields.Many2one('res.partner', string='Partner')
    room_type_info_ids = fields.One2many('room.type.information','room_type_info_id', string='Room Type Information')
    image_11 = fields.Binary(string='Hotel Img 1')
    image_12 = fields.Binary(string='Hotel Img 2')
    image_13 = fields.Binary(string='Hotel Img 3')
    image_14 = fields.Binary(string='Hotel Img 4')
    
    @api.model
    def create(self, values):
        res = super(AccomodationInformation, self).create(values)
        if values.get('name'): 
            partner = self.env['res.partner'].create(
                {'name': values.get('name'),
                'email': values.get('email'),
                'phone': values.get('phone'),
                })
            res.partner_id = partner.id
        return res
    
    def write(self, vals):
        res = super().write(vals)
        if 'name' in vals:
            self.partner_id.write({'name': vals['name']})
        if 'email' in vals:
            self.partner_id.write({'email': vals['email']})
        if 'phone' in vals:
            self.partner_id.write({'phone': vals['phone']})
        return res
    
    
    
