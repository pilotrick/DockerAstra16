from odoo import api, fields, models
from odoo import exceptions
from odoo.exceptions import ValidationError
from datetime import timedelta


class PropertyOffer(models.Model):
    _name = 'property.offer'

    price = fields.Float(string='Price')
    offer_status = fields.Selection(selection=[('new', 'New'), ('reject', 'Rejected'), (
        'accept', 'Accepted')], copy=False, string='Status', default='new')
    partner_id = fields.Many2one('res.partner', string='Partner Id')
    expected_days = fields.Integer('Expected Days', default=7)
    deadlines = fields.Date(string='Deadlines',
                            compute="_date_to_days_converter",
                            inverse="_days_to_date_converter")
    email = fields.Char(string='Email', required=True)

    property_id = fields.Many2one(
        'real.estate', string='Property Id', invisible=True)
    salesman = fields.Many2one(related ='property_id.salesmen')
    property_type_id = fields.Many2one(
        'property.type', string='Property Type Id', related="property_id.property_type_id")

    tax = fields.Float()
    admin_charge = fields.Float()
    total = fields.Float()
    
    # # sql constraints
    # _sql_constraints = [
    #     ('check_price', 'CHECK(price > 0)', 'Price Must Be Positive Number.'),
    #     ('check_expected_days', 'CHECK(expected_days > 0)', 'Expected Days Must Be Positive Number.'),
    #     ('check_deadlines', 'CHECK(deadlines < property_id.date_availability )', 'Deadline Must Be Select After Availability Date.'),
    # ]
    
    # constrains for price
    @api.onchange('price')
    def _check_price(self):
        for rec in self:
            if rec.price < 0 :
                raise exceptions.UserError(
                    ('Price must be positive number')
                    )

    # constrains for expected days      
    @api.onchange('expected_days')
    def _check_expected_days(self):
        for rec in self:
            if rec.expected_days >= 0 :
                pass
            else :
                raise exceptions.UserError(
                    ('Expected days must be more then 0')
                    )
    
    # check deadlines is after date availablity            
    @api.onchange('deadlines')
    def _check_bedrooms(self):
        for rec in self:
            if rec.deadlines >= rec.property_id.date_availability :
                pass
            else :
                raise exceptions.UserError(
                    ('Deadlines must be more then availability date')
                    )

    # offer accept
    def on_accept(self):
        for rec in self:
            if 'accept' in rec.property_id.new_offers.mapped('offer_status'):
                raise exceptions.UserError(('Can not Accept anoteher offer for same property'))
            else :
                rec.tax = (rec.price + 6)/100
                rec.admin_charge = 100
                rec.total = rec.price + rec.admin_charge + rec.tax
                
                rec.property_id.selling_price = rec.price
                rec.property_id.state = 'offer_accepted'
                rec.property_id.buyer = rec.partner_id.id
                
                rec.offer_status = 'accept'
                                
                template_id = self.env.ref('real_estate_bs.property_offer_accepted_email').id
                template = self.env['mail.template'].browse(template_id)
                template.send_mail(self.id, force_send=True)

    # offer reject
    def on_reject(self):
        for rec in self:
            if rec.offer_status == 'new':
                rec.offer_status = 'reject'
                
                template_id = self.env.ref('real_estate_bs.property_offer_rejected_email').id
                template = self.env['mail.template'].browse(template_id)
                template.send_mail(self.id, force_send=True)
                
            elif rec.offer_status == 'accept':
                raise exceptions.UserError(('Offer already accepted'))
            else:
                raise exceptions.UserError(('offer already rejected'))

    # check price is Higher then expected price 
    @api.constrains('price')
    def _check_price(self):
        for rec in self:
            if rec.price < (rec.property_id.expected_price * 90)/100:
                raise ValidationError(
                    "You can not enter amount less then 90/% /of expected amount ")

    # change state when offer recived
    @api.constrains('price')
    def _state_change(self):
        for rec in self:
            if rec.price:
                rec.property_id.state = 'offer_received'

    # change deadlines according to date availablity ad expected days
    @api.onchange('property_id.date_availability', 'expected_days')
    def _date_to_days_converter(self):
        for rec in self:
            if rec.property_id.date_availability:
                rec.deadlines = rec.property_id.date_availability + \
                    timedelta(days=rec.expected_days)

    # change expected days when deadlined added 
    @api.onchange('deadlines')
    def _days_to_date_converter(self):
        for rec in self:
            if rec.deadlines:
                rec.expected_days = (
                    rec.deadlines - rec.property_id.date_availability).days
                