from odoo import models, fields, api

class TravelInformation(models.Model):
    _name = 'travel.info'
    _inherit = 'mail.thread'
    _description = 'Travel Info'

    from_place = fields.Many2one('place.place', string='From')
    to_place = fields.Many2one('place.place', string='TO')
    transport_type =fields.Char(string='Transport Type')
    travel_class = fields.Char(string='Travel Class')
    distance_in_km = fields.Char(string='Distance in KM')
    time_hrs = fields.Char(string='Duration Time(Hrs)')
    from_place_id = fields.Many2one("custom.tour")
