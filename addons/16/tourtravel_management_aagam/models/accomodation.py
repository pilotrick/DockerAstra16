# -*- coding: utf-8 -*-
from odoo import models, fields, _, api


class RoomType(models.Model):
    _name = 'room.type'
    _inherit = 'mail.thread'
    _description = 'Room Type'

    name = fields.Char(
        string='name', required="1", tracking=True)


class Meal(models.Model):
    _name = 'meal.meal'
    _inherit = 'mail.thread'
    _description = 'Meal for the booked accomodation'

    name = fields.Char(string='Name', tracking=True)


class Accommodation(models.Model):
    _name = 'booking.accommodation'
    _inherit = 'mail.thread'
    _description = 'Booking Accommodation details'
    
    def name_get(self):
        result = []
        for res in self:
            if res.hotel_id:
                name = res.hotel_id.name
            result.append((res.id, name))
        return result

    name = fields.Char(
        string='name',
        tracking=True)
    hotel_id = fields.Many2one('accomodation.information', string='Hotel Name')
    tour_id = fields.Many2one('custom.tour')
    date_in = fields.Date(
        string='Date IN', help='Date checked-in', tracking=True)
    date_out = fields.Date(
        string='Date OUT', help='Date checked-out',
        tracking=True)
    room_type_id = fields.Many2one(
        comodel_name='room.type', string='Room Type', help='Room Type',
        tracking=True)
    no_of_pax = fields.Integer(
        string='Number of Pax', tracking=True)
    meal_id = fields.Many2one(
        comodel_name='meal.meal', string='Meal', tracking=True)
    booked_by_id = fields.Many2one(
        comodel_name='res.partner', string='Booked By',
        help='Agent or customer for the accommodation booking',
        tracking=True)
    other_detail = fields.Text(
        string='Other Details', tracking=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency',
        tracking=True, related='tour_reservation_id.currency_id')
    cost_ids = fields.Many2many(
        'persontype.cost', 'accomodation_person_cost', 'accomodation_id',
        'cost_id', string='Cost', tracking=True)
    tour_reservation_id = fields.Many2one(
        comodel_name='tour.reservation', string='Tour Reservation',
        help='Booking accommodation is for which tour booking',
        tracking=True)
    tour_ids = fields.Many2one('custom.tour', string='Tour Name')
    tour_start_date = fields.Date(string='Tour Start Date', related='tour_ids.tour_details_id.start_date')
    cost_price = fields.Char(string='Cost Price')
    sale_price = fields.Char(string='Sale Price')

    def action_send_email_to_hotel(self):
        self.ensure_one()
        template = self.env.ref('tourtravel_management_aagam.email_template_accomodation')
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        ctx = dict(
            default_model='booking.accommodation',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            custom_layout="mail.mail_notification_light",
            default_partner_ids=self.hotel_id and self.hotel_id.partner_id.ids or False,
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
        
