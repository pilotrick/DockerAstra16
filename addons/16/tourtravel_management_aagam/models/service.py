# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Service(models.Model):
    _name = 'booking.service'
    _inherit = 'mail.thread'
    _description = 'Booking Service'

    @api.model
    def default_get(self, default_fields):
        res = super(Service, self).default_get(default_fields)
        if res.get('tour_reservation_id'):
            tour_reservation = self.env['tour.reservation'].sudo().search(
                [('id', '=', res.get('tour_reservation_id'))])
            customer_name_ids = tour_reservation.booking_info_ids.mapped(
                'person_info_ids.name.id')
            if customer_name_ids:
                res.update({'customer_name_ids': customer_name_ids})
        return res

    @api.depends('cost_ids')
    def _compute_invoiced_qty(self):
        for service in self:
            total = 0
            if service.cost_ids:
                total = 0
                for cost in service.cost_ids:
                    total += cost.cost
            service.qty_invoiced = total
            # invoice_lines = service.cost_ids.mapped('invoice_line_ids')
            # invoice_lines = invoice_lines.filtered(
            #     lambda l: l.move_id and l.move_id.state != 'cancel' and
            #     l.move_id.tour_reservation_id.id == service.tour_reservation_id.id)
            # qty_invoiced = sum(invoice_lines.mapped('quantity'))
            # service.qty_invoiced = qty_invoiced

    name = fields.Char(string="Service name", tracking=True)
    tour_id = fields.Many2one('custom.tour')
    service_datetime = fields.Date(
        string='Datetime', help='Service Datetime',
        tracking=True)
    no_of_pax = fields.Integer(
        string='Number of Pax', tracking=True)
    qty_invoiced = fields.Float(
        string='Qty Invoiced',compute="_compute_invoiced_qty",
        store=True)
    customer_name_ids = fields.Many2many(
        comodel_name='res.partner', string='Passenger Names',
        tracking=True)
    place_from = fields.Many2one(
        'place.place', string='From', help='Place from where service starts',
        tracking=True)
    place_to = fields.Many2one(
        'place.place', string='To', help='Place to where service ends',
        tracking=True)
    driver_id = fields.Many2one(
        comodel_name='res.partner', string='Driver',
        help="Driver person for the service", domain="[('driver', '=', True)]",
        tracking=True)
    guide_id = fields.Many2one(
        comodel_name='res.partner', string='Guide',
        help='Guide person for the service', domain="[('guide', '=', True)]",
        tracking=True)
    service_remarks = fields.Text(
        string='Service Remarks', tracking=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency',
        tracking=True, related='tour_reservation_id.currency_id')
    cost_ids = fields.Many2many(
        'persontype.cost', 'service_person_cost', 'service_id', 'cost_id',
        string='Cost', tracking=True)
    tour_reservation_id = fields.Many2one(
        comodel_name='tour.reservation', string='Tour Reservation',
        help='Booking service is for which tour booking',
        tracking=True)
    day_sheet_id = fields.Many2one(
        comodel_name='day.sheet', string='Day Sheet')

    @api.model
    def create(self, values):
        res = super(Service, self).create(values)
        if self._name == 'booking.service':
            for service in res:
                day_sheet = self.env['day.sheet'].create(
                    {'tour_reservation_id': res.tour_reservation_id.id,
                     'service_id': res.id})
                service.day_sheet_id = day_sheet.id
        else:
            for service in res:
                day_sheet = self.env['day.sheet'].create(
                    {'tour_reservation_id': res.tour_reservation_id.id,
                     'extra_service_id': res.id})
                service.day_sheet_id = day_sheet.id
        return res

    @api.constrains('cost_ids', 'no_of_pax')
    def _check_reconcile(self):
        for service in self:
            if sum(service.cost_ids.mapped('no_of_pax')) > service.no_of_pax:
                raise ValidationError(
                    _("You can not set more"
                      " than number-of-pax defined in service-'%s'") % (
                      service.name))

    # @api.onchange('place_from', 'place_to')
    # def onchange_place_from_to(self):
    #     name = '%s %s %s' % (
    #         self.place_from.name or '', 'to' if self.place_to else '',
    #         self.place_to.name or '')
    #     self.name = name

    @api.model
    def generate_service_daysheet(self):
        for rec in self.env['booking.service'].search([
                ('day_sheet_id', '=', False),
                ('tour_reservation_id', '!=', False)]):
            day_sheet = self.env['day.sheet'].create({
                'tour_reservation_id': rec.tour_reservation_id.id,
                'service_id': rec.id})
            rec.day_sheet_id = day_sheet.id


class ExtraService(models.Model):
    _name = 'booking.extra.service'
    _inherit = 'booking.service'
    _description = 'Extra booking service'

    agent_id = fields.Many2one(
        comodel_name='res.partner', string='Agent',
        domain="[('s_agent', '=', 'parent'), ('parent_id', '=', False)]",
        tracking=True)
    tour_id = fields.Many2one('custom.tour')
    sub_agent_id = fields.Many2one(
        comodel_name='res.partner', string='Sub Agent',
        domain="[('s_agent', '=', 'child')]",
        tracking=True)
    tour_consultant_id = fields.Many2one(
        comodel_name='res.partner', string='Tour Consultant',
        domain="[('tour_consultant', '=', True)]", tracking=True)
    cost_ids = fields.Many2many(
        'persontype.cost', 'extra_service_person_cost', 'extra_service_id',
        'cost_id', string='Cost', tracking=True)
    day_sheet_id = fields.Many2one(
        comodel_name='day.sheet', string='Day Sheet')

    @api.constrains('cost_ids', 'no_of_pax')
    def _check_reconcile(self):
        for service in self:
            if sum(service.cost_ids.mapped('no_of_pax')) > service.no_of_pax:
                raise ValidationError(
                    _("You can not set more"
                      " than number-of-pax defined in extra-service-'%s'") % (
                      service.name))

    @api.model
    def generate_extra_service_daysheet(self):
        for rec in self.env['booking.extra.service'].search([
                ('day_sheet_id', '=', False),
                ('tour_reservation_id', '!=', False)]):
            day_sheet = self.env['day.sheet'].create({
                'tour_reservation_id': rec.tour_reservation_id.id,
                'extra_service_id': rec.id})
            rec.day_sheet_id = day_sheet.id
