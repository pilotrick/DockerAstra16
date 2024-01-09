
from odoo import models, fields, api ,_
import datetime

class TourItinerary(models.Model):
    _name = 'tour.itinerary'
    _inherit = 'mail.thread'

    name = fields.Char(string='Name')
    customer_inquiry_id = fields.Many2one('tour.inquiry', string="Customer Inquiry", required=True)
    tour_lead = fields.Many2one('res.partner', string='Lead', related="customer_inquiry_id.lead")
    tour_id = fields.Many2one('custom.tour', string='Tour', required=True)
    street = fields.Char('Street', related='customer_inquiry_id.street')
    street2 = fields.Char('Street2', related='customer_inquiry_id.street2')
    zip = fields.Char('Zip', change_default=True, related='customer_inquiry_id.zip')
    city = fields.Char('City', related='customer_inquiry_id.city')
    state_id = fields.Many2one("res.country.state", string='State', related='customer_inquiry_id.state_id')
    country_id = fields.Many2one('res.country', string='Country', related='customer_inquiry_id.country_id')
    contact_name = fields.Many2one('res.partner', string='Contact Name', related='customer_inquiry_id.contact_name')
    email = fields.Char(string='Email Id', related='customer_inquiry_id.email_id')
    mobile = fields.Char(string='Mobile', related='customer_inquiry_id.mobile')
    tour_via = fields.Char(string='Reference', related='customer_inquiry_id.tour_via')
    stat_date =fields.Date(string='Prefer Start Date', related='customer_inquiry_id.stat_date')
    end_date =fields.Date(string='Prefer End Date', related='customer_inquiry_id.end_date')
    room_required = fields.Char(string='Room Required')
    usd_currency_id =fields.Many2one('res.currency', string='Currency')
    payment_term_id = fields.Many2one('tour.payment.policy', string='Payment policy')
    tour_details_id = fields.One2many('tour.details', 'season_tour')
    adult_tour = fields.Char(string='Adults', related='customer_inquiry_id.adult_tour')
    chiid_tour = fields.Char(string='Childs' ,related='customer_inquiry_id.chiid_tour')
    start_date_tour = fields.Date(string='Start Date', related='tour_id.tour_details_id.start_date')
    last_date_booking = fields.Date(string='Booking Last Date', related='tour_id.tour_details_id.last_date_booking')
    payment_due_date = fields.Date(string='Payment Due Date', related='tour_id.tour_details_id.payment_due_date')
    total_seats = fields.Char(string='Total Seats', related='tour_id.tour_details_id.total_seats')
    tour_program_id = fields.One2many('tour.program','tour_code_program')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('approve', 'Approved'),
            ('done', 'Done')
        ], string='Status', help='Status of the tour reservation',
        default='draft', tracking=True)
    total_no_of_pax = fields.Integer(
        string='Total Number of Pax', tracking=True,compute="_def_compute_total_pax")
    booking_date = fields.Date(string='Booking Date')
    tour_type = fields.Char(string='Tour Type', related='tour_id.tour_type')
    tour_season = fields.Char(string='Tour Season', related='tour_id.tour_details_id.season_tour')
    remarks = fields.Text(
        string='Remarks', help='comment/remarks for the customer',
        tracking=True)
    person_info_ids = fields.Many2many(
        comodel_name='booking.person.information', string='Person Information')
    book_accomodation_id = fields.Many2one("booking.accommodation")
    voucher_no = fields.Char("Voucher Number")
    total_cost_tour = fields.Float("Total Cost Of Tour")

    _sql_constraints = [
        ('voucher_no_uniq', 'UNIQUE (voucher_no)', 'Voucher number already created !')
    ]

    def action_create_invoice(self):
        if self:
            account = self.env['account.account'].search([('company_id', '=', self.env.company.id)], limit=1)
            product_nm  = "Tour For"+ " "+ self.tour_id.name
            invoice_id = self.env['account.move'].create({
                'partner_id':self.contact_name.id,
                'move_type': 'out_invoice',
                # 'l10n_in_gst_treatment':self.contact_name.l10n_in_gst_treatment or "",
                'payment_reference':self.name,
                'invoice_date': fields.Datetime.now(),
                })
            invoice_id.write({
                'invoice_line_ids': [
                    (0, 0, {
                        'name':product_nm,
                        'quantity': 1,
                        'price_unit': self.total_cost_tour or 0.0,
                        'move_id': invoice_id.id,
                        'account_id': account.id,
                    })]})

    @api.depends('adult_tour','chiid_tour')
    def _def_compute_total_pax(self):
        self.total_no_of_pax = 0
        if (int(self.adult_tour) > 0 or int(self.chiid_tour) > 0):
            self.total_no_of_pax = (int(self.adult_tour) + int(self.chiid_tour))

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code(
            'tour.itinerary.seq') or '/'
        return super(TourItinerary, self).create(values)

    def action_confirmed(self):
        self.write({'state': 'confirmed'})

    def action_approve(self):
        self.write({'state': 'approve'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_create_tour(self):
        tour_form = self.env.ref('tourtravel_management_aagam.create_tour_form_views')
        return {
            'name': _('Create Tour'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'custom.tour',
            'views': [(tour_form.id, 'form')],
            'view_id': tour_form.id,
            'target': 'new',
            'context': {},
        }

    def action_quotation_send(self):
        self.ensure_one()
        template = self.env.ref('tourtravel_management_aagam.email_template_itinerary')
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        ctx = dict(
            default_model='tour.itinerary',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            custom_layout="mail.mail_notification_light",
            default_partner_ids=self.contact_name and self.contact_name.ids or False,
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


class TourProgram(models.Model):
    _name = 'tour.program'

    name = fields.Char(string='Name')
    tour_id = fields.Many2one('custom.tour', string='Tour')
    tour_code_program = fields.Char(string='Tour Code', related='tour_id.tour_code')
    tour_days = fields.Char(string='Tour Days')
    tour_nights = fields.Char(string='Tour Nights')
    tour_days_description = fields.Text(string='Tour Days Description')
    tour_breakfast = fields.Boolean(string='Breakfast')
    tour_lunch = fields.Boolean(string="Lunch")
    tour_dinner = fields.Boolean(string="Dinner")

class TourInquiry(models.Model):
    _name = 'tour.inquiry'
    _inherit = 'mail.thread'

    name = fields.Char(string='Name', default='/', tracking=True)
    tour_inquiry_date = fields.Date(string='Tour Inquiry Date', required=True)
    lead = fields.Many2one('res.partner',string='Lead By', required=True)
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', change_default=True)
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country')
    email_id = fields.Char(string='Email Id', required=True)
    mobile = fields.Char(string='Mobile', required=True)
    contact_name = fields.Many2one('res.partner', string='Contact Name', required=True)
    adult_tour = fields.Char(string='Number Of Adult')
    chiid_tour = fields.Char(string='Number Of Child')
    tour_via = fields.Char(string='Reference')
    stat_date = fields.Date(string='Prefer Start Date')
    end_date = fields.Date(string='Prefer End Date')
    budget_person_min = fields.Char(string='Budget/Person min')
    budget_person_max = fields.Char(string='Budget/Person max')
    confirme_budget = fields.Char(string='Confirmed Budget')
    notes = fields.Text(string='Notes')
    destination_id = fields.One2many('tour.inquiry.line', 'name')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
        ], string='Status', help='Status of the tour reservation',
        default='draft', tracking=True)

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code(
            'tour.inquiry.seq') or '/'
        return super(TourInquiry, self).create(values)

    def action_confirmed(self):
        self.write({'state': 'confirmed'})


class TourInquiryLine(models.Model):
    _name = 'tour.inquiry.line'

    name = fields.Char('Name', invisible="1")
    tour_destination = fields.Char(string='Destination')
    tour_country = fields.Many2one('res.country', string='Country')
    Number_of_night = fields.Char(string='No Of Nights')
    number_of_days = fields.Char(string='No Of Days')
    tour_location = fields.Many2many('place.place', string='Location')


class TourPaymentPolicy(models.Model):
    _name = 'tour.payment.policy'

    name = fields.Char(string="name")
