# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class TourCreate(models.Model):
    _name = 'custom.tour'

    name = fields.Char(string='Tour Name')
    tour_type = fields.Char(string='Tour Type')
    tour_code = fields.Char(string='Tour Code')
    Date_of_publish = fields.Date(string='Date Of Publish')
    days = fields.Char(string="Tour days")
    tour_plans =fields.Char()
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'), ('cancel', 'Cancel')
        ], string='Status', help='Status of the tour reservation',
        default='draft', tracking=True)
    travel_info_ids = fields.One2many('travel.info', 'from_place_id')
    tour_details_id = fields.One2many('tour.details', 'tour_id')
    tour_service_id = fields.One2many('booking.service', 'tour_id')
    tour_accommodation_id = fields.One2many('booking.accommodation', 'tour_id')
    tour_flight_id = fields.One2many('flight.flight', 'tour_id')
    tour_extra_services_id = fields.One2many('booking.extra.service', 'tour_id')
    reservation_id = fields.Many2one('tour.reservation')


    def action_confirmed(self):
        self.write({'state': 'confirmed'})

class TourCustom(models.Model):
    _name = 'tour.details'

    name = fields.Char(string='Name')
    tour_id = fields.Many2one('custom.tour')
    season_tour = fields.Char(string='Tour Season')
    start_date = fields.Date(string='Start Date')
    last_date_booking = fields.Date(string='Last Date Of Booking')
    payment_due_date = fields.Date(string='Payment Due Date')
    total_seats = fields.Char(string='Total Seats')
    available_seats = fields.Char(string='Available Seats')
    status = fields.Char(string='Status')
