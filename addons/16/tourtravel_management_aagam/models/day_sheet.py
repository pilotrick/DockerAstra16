# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api
from collections import OrderedDict


class DaySheet(models.Model):
    _name = 'day.sheet'
    _inherit = 'mail.thread'
    _description = 'Day sheet for the tour bookings'
    _rec_name = 'tour_reservation_id'

    @api.depends('service_ids', 'service_ids.service_datetime')
    def _compute_service_dates(self):
        for rec in self:
            service_start = rec.service_ids.sorted(
                lambda s: s.service_datetime)
            service_end = rec.service_ids.sorted(
                lambda s: s.service_datetime, reverse=True)
            rec.service_start = service_start[0].service_datetime if \
                service_start else ''
            rec.service_end = service_end[0].service_datetime if \
                service_end else ''

    @api.depends('extra_service_ids', 'extra_service_ids.service_datetime')
    def _compute_extra_service_dates(self):
        for rec in self:
            service_start = rec.extra_service_ids.sorted(
                lambda s: s.service_datetime)
            service_end = rec.extra_service_ids.sorted(
                lambda s: s.service_datetime, reverse=True)
            rec.extra_service_start = service_start[0].service_datetime if \
                service_start else ''
            rec.extra_service_end = service_end[0].service_datetime if \
                service_end else ''

    @api.depends('extra_service_id', 'extra_service_id.service_datetime',
                 'service_id', 'service_id.service_datetime')
    def _compute_service_date(self):
        for rec in self:
            # service
            if rec.service_id:
                rec.service_date = rec.service_id.service_datetime
                rec.s_datetime = rec.service_id.service_datetime

            # # extra service
            if rec.extra_service_id:
                rec.extra_service_date = rec.extra_service_id.service_datetime
                rec.s_datetime = rec.extra_service_id.service_datetime

    # tour_reservation
    tour_reservation_id = fields.Many2one(
        comodel_name='tour.reservation', string='Tour Reservation', ondelete="cascade", tracking=True)

    # tour reservation service
    # to create record per tour-reservation service / extra-service
    service_id = fields.Many2one(
        comodel_name='booking.service', string='Service', ondelete="cascade",
        help='Service for the tour reservation, only one tour booking service',
        domain="[('id', 'in', service_ids)]", tracking=True)
    service_datetime = fields.Date(
        string='datetime', help='Service Datetime',
        tracking=True, related="service_id.service_datetime",
        store=True)
    service_date = fields.Date(
        string='Service Date', help='Service Date',
        compute='_compute_service_date', store=True)
    extra_service_id = fields.Many2one(
        comodel_name='booking.extra.service', string='Extra Service',
        help='Extra Service for the tour reservation',
        tracking=True, ondelete="cascade",
        domain="[('id', 'in', extra_service_ids)]")
    extra_service_datetime = fields.Date(
        string='Datetime', help='Extra-Service Datetime',
        tracking=True,
        related="extra_service_id.service_datetime", store=True)
    extra_service_date = fields.Date(
        string='Extra Service Date', help='Extra Service Date',
        compute='_compute_service_date', store=True)
    s_datetime = fields.Date(
        string='Service general Datetime', help='Extra/Service Date',
        compute='_compute_service_date', store=True)

    service_ids = fields.One2many(
        comodel_name='booking.service', string="Tour Services",
        related="tour_reservation_id.service_ids", tracking=True)
    extra_service_ids = fields.One2many(
        comodel_name='booking.extra.service', string="Tour Extra-Services",
        related="tour_reservation_id.extra_service_ids",
        tracking=True)
    booking_name = fields.Char(
        string='Booking Name', related="tour_reservation_id.booking_name",
        tracking=True)
    booking_date = fields.Date(
        string='Booking Date', related="tour_reservation_id.booking_date",
        tracking=True)
    agent_id = fields.Many2one(
        comodel_name='res.partner', string='Agent',
        domain="[('s_agent', '=', 'parent')]",
        related='tour_reservation_id.agent_id', tracking=True)
    driver_id = fields.Many2one(
        comodel_name='res.partner', string='Driver',
        help="Driver person for the service", domain="[('driver', '=', True)]",
        tracking=True,related='tour_reservation_id.service_ids.driver_id')
    guide_id = fields.Many2one(
        comodel_name='res.partner', string='Guide',
        help='Guide person for the service', domain="[('guide', '=', True)]",
        tracking=True,related='tour_reservation_id.service_ids.guide_id')
    file_number = fields.Char(
        string='File Number', related='tour_reservation_id.file_number',
        tracking=True)
    state = fields.Selection(string='Status', related='tour_reservation_id.state',
                             tracking=True)
    remarks = fields.Text(
        string='Remarks', help='comment/remarks for the customer',
        tracking=True, related='tour_reservation_id.remarks')
    active = fields.Boolean(
        string='Active', related='tour_reservation_id.active',
        tracking=True)

    # compute fields for service-extra_service start and end datetime
    service_start = fields.Date(
        string='Service Start datetime', compute='_compute_service_dates',
        store=True)
    service_end = fields.Date(
        string='Service End datetime', compute='_compute_service_dates',
        store=True)
    extra_service_start = fields.Date(
        string='ExtraService Start datetime',
        compute='_compute_extra_service_dates', store=True)
    extra_service_end = fields.Date(
        string='ExtraService End datetime',
        compute='_compute_extra_service_dates', store=True)

    def approve_booking(self):
        self.write({'state': 'in_progress'})

    def confirm_booking(self):
        self.write({'state': 'confirmed'})

    @api.model
    def get_day_sheet_data(self, day_sheets=False):
        return_dict = {}
        domain = [('active', '=', True),
                  ('state', 'in', ['confirmed', 'done'])]
        if day_sheets:
            domain.append(('id', 'in', day_sheets.ids))
        day_sheet = self.search(domain)
        service_group = self.read_group([
            ('id', 'in', day_sheet.ids)
        ], [
            "id", "s_datetime"
        ], groupby="s_datetime:day", orderby="s_datetime")
        for sg in service_group:
            domain = sg.get('__domain')
            services = self.search(domain, order='s_datetime')
            if services:
                s_key = sg.get('s_datetime:day')
                return_dict.update({s_key: {'services': services}})
        return return_dict

    @api.model
    def get_today_day_sheet_data(self, day_sheets=False):
        today = fields.Date.context_today(self)
        service_obj = self.env['booking.service']
        extra_service_obj = self.env['booking.extra.service']
        return_dict = {}
        day_sheet = self.search([
            ('active', '=', True), ('state', 'in', ['confirmed', 'done']),
            '|',
            ('service_ids.service_datetime', '>=', today),
            ('extra_service_ids.service_datetime', '>=', today)])
        service_group = self.env['booking.service'].read_group([
            ('tour_reservation_id', 'in',
                day_sheet.mapped('tour_reservation_id.id')),
            ('service_datetime', '>=', today)], ["id", "service_datetime", ],
            groupby="service_datetime:day", orderby="service_datetime")
        for sg in service_group:
            domain = sg.get('__domain')
            services = service_obj.search(domain, order='service_datetime')
            if services:
                s_key = sg.get('service_datetime:day')
                return_dict.update({s_key: {'services': services}})

        extra_service_group = extra_service_obj.read_group([
            ('tour_reservation_id', 'in',
                day_sheet.mapped('tour_reservation_id.id')),
            ('service_datetime', '>=', today)], ["id", "service_datetime", ],
            groupby="service_datetime:day", orderby="service_datetime")
        for sg in extra_service_group:
            domain = sg.get('__domain')
            services = extra_service_obj.search(
                domain, order='service_datetime')
            if services:
                s_key = sg.get('service_datetime:day')
                if s_key in return_dict:
                    values = return_dict[s_key]
                    values.update({'extra_services': services})
                    return_dict.update({s_key: values})
                else:
                    return_dict.update({s_key: {'extra_services': services}})
        return_dict = OrderedDict(sorted(
            return_dict.items(), key=lambda t: t[0]))
        return return_dict
