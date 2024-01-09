# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.http import request
import calendar as cal
from odoo.exceptions import UserError
from datetime import date
import datetime
from datetime import timedelta


class Place(models.Model):
    _name = 'place.place'
    _description = 'Object used to store place name'

    name = fields.Char(
        string='Name', help='Name of the place', copy=False, required=True)


class PersonTypeCost(models.Model):
    _name = 'persontype.cost'
    _description = 'Object used to store cost per person type'
    _rec_name = 'person_type'

    @api.depends('invoice_line_ids', 'invoice_line_ids.move_id',
                 'invoice_line_ids.move_id.state')
    def _get_invoiced_qty(self):
        for rec in self:
            invoice_lines = rec.invoice_line_ids.filtered(
                lambda l: l.move_id.state != 'cancel')
            rec.qty_invoiced = sum(invoice_lines.mapped('quantity'))

    person_type = fields.Selection(
        selection=[
            ('Adult', 'Adult'), ('Children', 'Children'),
            ('Infant', 'Infant')], string='Person Type', default='Adult',
        required=True)
    no_of_pax = fields.Integer(
        string='Number of Pax', tracking=True)
    cost = fields.Float(
        string='Cost', digits=(16, 2), help='Cost per person',
        tracking=True, required=True)
    invoice_line_ids = fields.One2many(
        comodel_name='account.move.line', inverse_name='person_cost_id',
        string='Invoice Line', tracking=True,
        domain=[('move_id.state', '!=', 'cancel')])
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency',
        tracking=True, required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    qty_invoiced = fields.Float(
        string='Qty Invoiced', store=True)
        # string='Qty Invoiced', compute='_get_invoiced_qty', store=True)


class TourReservation(models.Model):
    _name = 'tour.reservation'
    _inherit = 'mail.thread'
    _description = 'Tour reservation details'
    _rec_name = 'file_number'

    def _get_invoiced(self):
        for tour in self:
            invoices = self.env['account.move'].search([
                ('tour_reservation_id', '=', tour.id),
                ('move_type', 'in', ['out_invoice', 'out_refund']), ])
            refund_invoices = self.env['account.move']
            for invoice in invoices:
                refund_invoices += self.env['account.move'].search([
                    ('invoice_origin', 'like', invoice.name),
                    ('move_type', 'in', ('out_invoice', 'out_refund'))])
            all_invoices = invoices + refund_invoices
            qty_invoiced = sum(tour.service_ids.mapped('qty_invoiced') +
                               tour.extra_service_ids.mapped('qty_invoiced'))
            total_qty = sum(tour.service_ids.mapped('no_of_pax') +
                            tour.extra_service_ids.mapped('no_of_pax'))
            qty_to_invoice = total_qty - qty_invoiced
            tour.update({'invoice_count': len(all_invoices),
                         'invoice_ids': all_invoices.ids,
                         'qty_to_invoice': qty_to_invoice})

    agent_file_number = fields.Char(
        string='Agent File Number', tracking=True)
    file_number = fields.Char(
        string='Booking/File Number', default='/', tracking=True)
    agent_id = fields.Many2one(
        comodel_name='res.partner', string='Agent',
        domain="[('s_agent', '=', 'parent'), ('parent_id', '=', False)]",
        tracking=True)
    sub_agent_id = fields.Many2one(
        comodel_name='res.partner', string='Sub agent',
        domain="[('s_agent', '=', 'child')]",
        tracking=True)
    booking_date = fields.Date(
        string='Booking Date', tracking=True,
        default=fields.Date.context_today, required=True)
    booking_name = fields.Char(
        string='Booking Name', tracking=True)
    active = fields.Boolean(
        string='Active', default=True, tracking=True)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'), ('in_progress', 'In Progress / Approval'),
            ('confirmed', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancel')
        ], string='Status', help='Status of the tour reservation',
        default='draft', tracking=True)
    day_sheet_id = fields.Many2one(
        comodel_name='day.sheet', string='Day Sheet',
        tracking=True)
    day_sheet_ids = fields.One2many(
        comodel_name='day.sheet', inverse_name='tour_reservation_id',
        string='day Shets',
        help="To store created day sheet for the tour reservation")
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency',
        tracking=True, required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    invoice_ids = fields.Many2many(
        "account.move", string='Invoices', compute="_get_invoiced",
        readonly=True, copy=False)
    invoice_count = fields.Integer(
        string='# of Invoices', compute='_get_invoiced', readonly=True)
    qty_to_invoice = fields.Float(
        string='Qty to Invoice', compute='_get_invoiced', readonly=True)
    remarks = fields.Text(
        string='Remarks', help='comment/remarks for the customer',
        tracking=True)


    _sql_constraints = [
        ('agent_file_number_uniq', 'unique (agent_file_number)',
         'The File number must be unique.')]

    @api.model
    def get_count_list(self):
        today = date.today()
        date_list = []
        last_month = []
        first = today.replace(day=1)

        last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
        start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)

        sdate = start_day_of_prev_month  # start date
        edate = last_day_of_prev_month  # end date

        delta = edate - sdate  # as timedelta
        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)
            last_month.append(day)

        lastMonth = first - datetime.timedelta(days=1)
        month_last = lastMonth.strftime("%Y-%m")
        tour_last_month = self.env['tour.reservation'].sudo().search_count([('booking_date', 'in', last_month)])
        for i in range(7, 14):
            last_week_date = today - timedelta(days=i)
            date_list.append(last_week_date)
        total = self.env['tour.reservation'].sudo().search_count([('booking_date', 'in', date_list)])

        total_booking = self.env['tour.reservation'].sudo().search_count([])
        today_booking = self.env['tour.reservation'].sudo().search_count([('booking_date', '=', fields.Date.today())])
        return {
            'today_booking': today_booking,
            'total_booking': total_booking,
            'last_week': total,
            'last_month': tour_last_month,

        }

    @api.model
    def get_weekly_booking(self):
        cr = self._cr

        query = """
             SELECT booking_date FROM tour_reservation

             """
        cr.execute(query)
        partner_data = cr.dictfetchall()
        partner_day = []
        data_set = {}
        mydate = []
        mycount = []
        list_value = []
        dict = {}
        count = 0
        days = ["Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday", "Sunday"]
        for data in partner_data:
            if data['booking_date']:
                mydate = data['booking_date'].weekday()
                if mydate >= 0:
                    value = days[mydate]
                    list_value.append(value)

                    list_value1 = list(set(list_value))

                    for record in list_value1:
                        count = 0
                        for rec in list_value:
                            if rec == record:
                                count = count + 1
                            dict.update({record: count})
                        keys, values = zip(*dict.items())
                        data_set.update({"data": dict})

        return data_set

    @api.model
    def get_monthly_booking(self):
        cr = self._cr

        query = """
                    SELECT booking_date FROM tour_reservation

                    """
        cr.execute(query)
        partner_data = cr.dictfetchall()
        partner_day = []
        data_set = {}
        mycount = []
        list_value = []

        dict = {}
        count = 0

        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                  'August', 'September', 'October', 'November', 'December']

        for data in partner_data:
            if data['booking_date']:
                mydate = data['booking_date'].month
                for month_idx in range(0, 13):
                    if mydate == month_idx:
                        value = cal.month_name[month_idx]
                        list_value.append(value)
                        list_value1 = list(set(list_value))
                        for record in list_value1:
                            count = 0
                            for rec in list_value:
                                if rec == record:
                                    count = count + 1
                                dict.update({record: count})
                        keys, values = zip(*dict.items())
                        data_set.update({"data": dict})

        return data_set

    @api.onchange('sub_agent_id')
    def set_agent(self):
        if self.sub_agent_id:
            self.agent_id = self.sub_agent_id.parent_id.id
        else:
            self.agent_id = False

    @api.model
    def create(self, values):
        values['file_number'] = self.env['ir.sequence'].next_by_code(
            'tour.booking.seq') or '/'
        return super(TourReservation, self).create(values)

    def action_approve(self):
        self.write({'state': 'in_progress'})

    def action_confirmed(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_invoice(self):
        self.ensure_one()
        inv_obj = self.env['account.move']
        inv_line_obj = self.env['account.move.line']

        if not self.service_ids:
            raise UserError(_("There is no service included.\
                Please include at least one service to create invoice."))

        if sum(self.mapped('service_ids.cost_ids.no_of_pax')) < sum(
                self.mapped('service_ids.no_of_pax')):
            raise UserError(
                _("Please define cost in the service for the "
                  "specified Number of pax."))

        if sum(self.mapped('extra_service_ids.cost_ids.no_of_pax')) < sum(
                self.mapped('extra_service_ids.no_of_pax')):
            raise UserError(
                _("Please define cost in the extra-service for "
                  "the specified Number of pax."))

        invoice_values = {
            'name': self.file_number,
            'invoice_origin': self.file_number,
            'move_type': 'out_invoice',
            'partner_id': self.agent_id.id,
            'invoice_date': fields.Date.today(),
            'agent_id': self.agent_id.id,
            'client_name': self.booking_name,
            'agent_reference': self.agent_file_number,
            'tour_reservation_id': self.id,
            'currency_id': self.currency_id.id,
        }
        config_parameter = self.env['ir.config_parameter'].sudo()
        service_product = config_parameter.get_param(
            'tourtravel_management_aagam.service_product')
        extra_service_product = config_parameter.get_param(
            'tourtravel_management_aagam.extra_service_product')
        # default_accomodation_product = config_parameter.get_param(
        #     'tourtravel_management_aagam.default_accomodation_product')
        # default_flight_product = config_parameter.get_param(
        #     'tourtravel_management_aagam.default_flight_product')
        # default_ferry_product = config_parameter.get_param(
        #     'tourtravel_management_aagam.default_ferry_product')
        invoice_ids = []
        e_service_inv = False
        service_inv = False
        if self.service_ids and sum(self.service_ids.mapped(
                'no_of_pax')) and sum(self.service_ids.mapped('qty_invoiced')):
            service_inv = inv_obj.with_context(
                mail_create_nosubscribe=True).create(invoice_values)
            invoice_ids.append(service_inv.id)
            for service in self.service_ids:
                qty_to_invoice = 0
                qty_to_invoice = service.no_of_pax - service.qty_invoiced
                name = '%s From: %s To: %s' % (
                    service.name, service.place_from.name,
                    service.place_to.name)
                for c in service.cost_ids.filtered(
                        lambda c: not c.invoice_line_ids):
                    new_line_values = {
                        'name': '%s %s' % (c.person_type, name),
                        'move_id': service_inv.id,
                        'product_id': int(service_product),
                        'price_unit': c.cost,
                        'service_datetime': service.service_datetime,
                        'quantity': c.no_of_pax,
                        'account_id': service_inv.id,
                        'person_cost_id': c.id,
                    }
                    # inv_line_obj.create(new_line_values)
                    service_inv.write({'invoice_line_ids': [(0, 0, new_line_values)]})
                service.qty_invoiced = service.qty_invoiced + qty_to_invoice

        if self.extra_service_ids and sum(
                self.extra_service_ids.mapped('no_of_pax')) > sum(
                    self.extra_service_ids.mapped('qty_invoiced')):
            e_service_inv = inv_obj.with_context(
                mail_create_nosubscribe=True).create(invoice_values)
            invoice_ids.append(e_service_inv.id)
            for service in self.extra_service_ids:
                qty_to_invoice = 0
                qty_to_invoice = service.no_of_pax - service.qty_invoiced
                name = '%s From: %s To: %s' % (
                    service.name, service.place_from.name,
                    service.place_to.name)
                for c in service.cost_ids.filtered(
                        lambda c: not c.invoice_line_ids):
                    new_line_values = {
                        'name': '%s %s' % (c.person_type, name),
                        'move_id': e_service_inv.id,
                        'product_id': int(extra_service_product),
                        'price_unit': c.cost,
                        'service_datetime': service.service_datetime,
                        'quantity': c.no_of_pax,
                        'account_id': e_service_inv.id,
                        'person_cost_id': c.id,
                    }
                    # inv_line_obj.create(new_line_values)
                    service_inv.write({'invoice_line_ids': [(0, 0, new_line_values)]})
                service.qty_invoiced = service.qty_invoiced + qty_to_invoice

        # if self.booking_accomodation_ids:
        #     new_inv = inv_obj.create(invoice_values)
        #     invoice_ids.append(new_inv.id)
        #     for accomodation in self.booking_accomodation_ids:
        #         new_line_values = {
        #             'name': accomodation.name.name,
        #             'invoice_id': new_inv.id,
        #             'product_id': int(default_accomodation_product),
        #             'price_unit': accomodation.cost,
        #             'service_datetime': accomodation.date_in,
        #             'quantity': 1.0,
        #             'account_id': new_inv.account_id.id
        #         }
        #         inv_line_obj.create(new_line_values)

        # if self.flight_ids:
        #     new_inv = inv_obj.create(invoice_values)
        #     invoice_ids.append(new_inv.id)
        #     for flight in self.flight_ids:
        #         new_line_values = {
        #             'name': flight.name.name,
        #             'invoice_id': new_inv.id,
        #             'product_id': int(default_flight_product),
        #             'price_unit': flight.cost,
        #             'service_datetime': flight.in_datetime,
        #             'quantity': 1.0,
        #             'account_id': new_inv.account_id.id
        #         }
        #         inv_line_obj.create(new_line_values)

        # if self.ferry_ids:
        #     new_inv = inv_obj.create(invoice_values)
        #     invoice_ids.append(new_inv.id)
        #     for ferry in self.ferry_ids:
        #         new_line_values = {
        #             'name': ferry.name,
        #             'invoice_id': new_inv.id,
        #             'product_id': int(default_ferry_product),
        #             'price_unit': ferry.cost,
        #             'service_datetime': ferry.in_datetime,
        #             'quantity': 1.0,
        #             'account_id': new_inv.account_id.id
        #         }
        #         inv_line_obj.create(new_line_values)

        if invoice_ids:
            self.write({
                'invoice_ids': invoice_ids
                })

            action = self.env.ref('account.action_move_out_invoice_type').read()[0]
            action['domain'] = [('id', 'in', invoice_ids)]
            return action
        else:
            raise UserError(
                _("Nothing to invoice:\nAll services are already invoiced."))

    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [
                (self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


class BookingPersonInformation(models.Model):
    _name = 'booking.person.information'
    _description = 'person details for the booking'
    _rec_name = 'name'

    name = fields.Many2one(
        comodel_name='res.partner', string='Name', help='Name of he person')
    age = fields.Integer(string='Age', help='Age of the person')
    gender = fields.Selection(
        selection=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        string='Gender', default='male')
    person_type = fields.Selection(
        selection=[
            ('Adult', 'Adult'), ('Children', 'Children'),
            ('Infant', 'Infant')], string='Person Type', default='Adult')


class BookingInformation(models.Model):
    _name = 'booking.information'
    _inherit = 'mail.thread'
    _description = 'Booking information'
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
    book_accomodation_id = fields.Many2one("booking.accommodation",domain="[('tour_reservation_id','=',tour_reservation_id),('tour_ids','=',tour_id)]")

    def action_quotation_send_booking_info(self):
        self.ensure_one()
        template = self.env.ref('tourtravel_management_aagam.email_template_booking_information')
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        ctx = dict(
            default_model='booking.information',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            custom_layout="mail.mail_notification_light",
            default_partner_ids=self.customer_id and self.customer_id.ids or False,
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
    @api.model
    def create(self, vals):
        booking_exist = self.env['booking.information'].search([
            ('tour_reservation_id', '=', vals.get('tour_reservation_id'))
            ], limit=1)

        if booking_exist:
            raise UserError(_("You can add only one booking per reservation."))

        res = super(BookingInformation, self).create(vals)
        return res
        return res

    def action_confirmed(self):
        self.write({'state': 'confirmed'})

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code(
            'tour.information.seq') or '/'
        return super(BookingInformation, self).create(values)

