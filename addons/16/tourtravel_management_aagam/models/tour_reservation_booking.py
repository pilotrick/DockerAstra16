# -*- coding: utf-8 -*-
from odoo import models, fields


class TourReservation(models.Model):
    _inherit = 'tour.reservation'

    booking_info_ids = fields.One2many(
        comodel_name='booking.information', inverse_name='tour_reservation_id',
        string='Booking Info', tracking=True)
    service_ids = fields.One2many(
        comodel_name='booking.service', inverse_name='tour_reservation_id',
        string='Services', tracking=True)
    extra_service_ids = fields.One2many(
        comodel_name='booking.extra.service',
        inverse_name='tour_reservation_id', string='Extra Services',
        tracking=True)
    booking_accomodation_ids = fields.One2many(
        comodel_name='booking.accommodation',
        inverse_name='tour_reservation_id', string='Accomodations',
        tracking=True)
    flight_ids = fields.One2many(
        comodel_name='flight.flight',
        inverse_name='tour_reservation_id', string='Flight',
        tracking=True)
    ferry_ids = fields.One2many(
        comodel_name='ferry.ferry',
        inverse_name='tour_reservation_id', string='Ferry',
        tracking=True)
    tour_ids = fields.One2many('custom.tour','reservation_id')
    tour_itinerary_ids = fields.One2many('tour.itinerary', 'name')
    tour_visa_id = fields.One2many('tour.visa', 'name')
    tour_passport_id = fields.One2many('visa.documentation', 'name')
