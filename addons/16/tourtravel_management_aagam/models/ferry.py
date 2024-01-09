# -*- coding: utf-8 -*-
from odoo import models, fields


class Ferry(models.Model):
    _name = 'ferry.ferry'
    _inherit = 'mail.thread'
    _description = 'Ferry'

    name = fields.Char(string="Ferry name", tracking=True)
    in_datetime = fields.Datetime(
        string='Date In and time', tracking=True)
    out_datetime = fields.Datetime(
        string='Date Out and time', tracking=True)
    place_from = fields.Many2one(
        'place.place', string='From', tracking=True)
    place_to = fields.Many2one(
        'place.place', string='To', tracking=True)
    booked_by_id = fields.Many2one(
        comodel_name='res.partner', string='Booked By',
        tracking=True)
    other_detail = fields.Text(
        string='Other Detail', tracking=True)
    tour_reservation_id = fields.Many2one(
        comodel_name='tour.reservation', string='Tour Reservation',
        help='Ferry detail is for which tour Booking',
        tracking=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency',
        tracking=True, related='tour_reservation_id.currency_id')
    cost_ids = fields.Many2many(
        'persontype.cost', 'ferry_person_cost', 'ferry_id', 'cost_id',
        string='Cost', tracking=True)
