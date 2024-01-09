# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime


class CustomBookingInformation(models.Model):
    _name = 'custom.booking.information'
    _inherit = 'mail.thread'
    _description = 'Custom Booking Information'
    _rec_name = 'tour_reservation_id'
    
    name = fields.Char(string='Name', default='/', tracking=True)
    customer_id = fields.Many2one('res.partner', string='Customer')
    email_id = fields.Char(string='Email Id')
    mobile_num = fields.Char(string='Mobile Number')
    booking_date = fields.Date(string='Booking Date')
    total_no_of_pax = fields.Integer(
        string='Total Number of Pax', tracking=True)
    total_adult = fields.Integer(
        string='Adult', help='Total adult person count',
        tracking=True)
    total_children = fields.Integer(
        string='Children', help='Total children count',
        tracking=True)
    total_infant = fields.Integer(
        string='Infant', help='Total infant count',
        tracking=True)
    remarks = fields.Text(
        string='Remarks', help='comment/remarks for the customer',
        tracking=True)
    tour_reservation_id = fields.Many2one(
        comodel_name='tour.reservation', string='Tour Reservation',
        help='Booking information is for which Tour reservation',
        tracking=True)
    person_info_ids = fields.Many2many(
        comodel_name='booking.person.information', string='Person Information')
    tour_id = fields.Many2one('custom.tour', string='Tour')
    tour_type = fields.Char(string='Tour Type', related='tour_id.tour_type')
    tour_start_date = fields.Date(string='Tour Start Date', related='tour_id.tour_details_id.start_date')
    payment_policy = fields.Many2one('tour.payment.policy', string='Payment Policy')
    tour_season = fields.Char(string='Tour Season', related='tour_id.tour_details_id.season_tour')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed')
        ], string='Status', help='Status of the tour reservation',
        default='draft', tracking=True)


    @api.model
    def create(self, vals):
        # booking_exist = self.env['booking.information'].search([
        #     ('tour_reservation_id', '=', vals.get('tour_reservation_id'))
        #     ], limit=1)

        # if booking_exist:
        #     raise UserError(_("You can add only one booking per reservation."))
        
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'custom.tour.booking.seq') or '/'

        return super(CustomBookingInformation, self).create(vals)

    def action_confirmed(self):
        self.write({'state': 'confirmed'})

    
    
