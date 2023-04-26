from odoo import api, fields, models,_
from odoo import exceptions
from odoo.exceptions import ValidationError
import random


class RealEstate(models.Model):
    _name = 'real.estate'

    # simple fields 
    name = fields.Char(string='name')
    postcode = fields.Char(string='Postcode')
    buyer = fields.Many2one('res.partner' ,string='Buyer', readonly=True, copy=False)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string="Phone Number", required=True , default='+917572869098')

    # date fields 
    date_availability = fields.Date(
        string='Date', default=fields.datetime.now())

    # float fields 
    expected_price = fields.Float(string='Expected Price')
    selling_price = fields.Float(string='Selling Price')
    best_offer = fields.Float(string='Best Offer',copy=False)

    # int fileds 
    bedrooms = fields.Integer(string='Bedrooms', default=2)
    living_area = fields.Integer(string='Living Area')
    facades = fields.Integer(string='Facades')
    garden_area = fields.Integer(string='Garden Area')
    total_area = fields.Integer(string='Total Area', compute='_total_area')

    # bool fields 
    garage = fields.Boolean(string='Garage')
    garden = fields.Boolean(string='Garden', default=False)

    # many2one fileds 
    tags = fields.Many2many('property.tags', string='tags')
    user_id = fields.Many2one('res.users', string='User Id')
    property_type_id = fields.Many2one('property.type')
    buyer_id = fields.Many2one('property.offer')
    salesmen = fields.Many2one(
        'res.users', string='Salesmen', readonly=True, default=lambda self: self.env.user)
    state_id = fields.Many2one('res.country.state', string = "State" )
    country_id = fields.Many2one('res.country', string = "Country", related="state_id.country_id")

    # one2many fields 
    new_offers = fields.One2many('property.offer', 'property_id', copy=False)

    # image fields 
    property_image = fields.Image(string='Image')

    # selection field
    state = fields.Selection(selection=[
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('cancel', 'Canceled')
    ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='new')
    garden_orientation = fields.Selection([('north', 'North'),
                                           ('south', 'South'),
                                           ('east', 'East'),
                                           ('west', 'West')], string='Garden Orientation', copy=False)
    
    #excel report
    summary_data = fields.Char('Name', size=256)
    file_name = fields.Binary('Pay Slip Summary Report', readonly=True)
    select_state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                            default='choose')
    # Generate barcode number 
    @api.model
    def _generate_code(self):
        return str(random.getrandbits(42))
    
    barcode = fields.Char(default=_generate_code, required=True, readonly=True)
    
    # # sql constraints
    # _sql_constraints = [('check_expected_price', 'CHECK(expected_price >= 0)', 'Expected Price Must Be Positive Number.'),
    #                     ('check_bedrooms', 'CHECK(bedrooms > 0)', 'Bedrooms Must Be Positive Number.'),
    #                     ('check_living_area', 'CHECK(living_area > 0 )','Living Area Must Be Select After Availability Date.'),
    #                     ('check_facades', 'CHECK(facades > 0 )', 'Facades Must Be Select After Availability Date.'),
    #                     ('check_garden_area', 'CHECK(garden_area > 0 )', 'Garden Area Must Be Select After Availability Date.')]

    # constrain for expected price 
    @api.onchange('expected_price')
    def _check_expected_price(self):
        for rec in self:
            if rec.expected_price >= 0:
                pass
            else:
                raise exceptions.UserError(
                    ('Enter positive Ammount')
                )


    # constrain for bedrooms 
    @api.onchange('bedrooms')
    def _check_bedrooms(self):
        for rec in self:
            if rec.bedrooms >= 1:
                pass
            else:
                raise exceptions.UserError(
                    ('Bedroom must be more then 1')
                )


    # constrain for living area 
    @api.onchange('living_area')
    def _check_living_area(self):
        for rec in self:
            if rec.living_area >= 0:
                pass
            else:
                raise exceptions.UserError(
                    ('Enter positive number')
                )


    # constrain for facades 
    @api.onchange('facades')
    def _check_facades(self):
        for rec in self:
            if rec.facades >= 0:
                pass
            else:
                raise exceptions.UserError(
                    ('Facades must be positive number')
                )


    # constrain for garden area
    @api.onchange('garden_area')
    def _check_garden_area(self):
        for rec in self:
            if rec.garden_area >= 0:
                pass
            else:
                raise exceptions.UserError(
                    ('Enter positive number')
                )


    # constrain for new offers
    @api.onchange('new_offers')
    def _count_best_offer(self):
        offers_in_home = [0]
        for rec in self.new_offers:
            offers_in_home.append(int(rec.price))

        self.best_offer = max(offers_in_home)

        # print('price : ', offers_in_home)
        # print('best offer : ', self.best_offer)


    # sold button action
    def action_do_sold(self):
        for rec in self:
            if rec.state == 'cancel':
                raise exceptions.UserError(
                    ('You can not sold canceled property')
                )
            elif rec.state == 'sold':
                raise exceptions.UserError(
                    ('Property Already Sold')
                )
            elif rec.state == 'new':
                raise exceptions.UserError(
                    ('First u have to select offer')
                )
            elif rec.state == 'offer_received':
                raise exceptions.UserError(
                    ('First u have to select offer')
                )
            else:
                rec.state = 'sold'
                notification = {
                                'type': 'ir.actions.client',
                                'tag': 'display_notification',
                                'params': {
                                            'title': _('Sold'),
                                            'type': 'success',
                                            'message': 'Your Property Sold',
                                            'sticky': False,
                                            }
                                }
                return notification


    # cancel button action
    def action_do_canceled(self):
        for rec in self:
            if rec.state == 'sold':
                raise exceptions.UserError(
                    ('You can not canceled sold property')
                )
            elif rec.state == 'cancel':
                raise exceptions.UserError(
                    ('Property Already Canceled')
                )
            else:
                rec.state = 'cancel'
                notification = {
                                'type': 'ir.actions.client',
                                'tag': 'display_notification',
                                'params': {
                                            'title': _('Cancel'),
                                            'type': 'warning',
                                            'message': 'Your Property Cancel',
                                            'sticky': False,
                                            }
                                }
                return notification
            
    #send report email
    def action_send_report_email(self):
        template_id = self.env.ref('real_estate_bs.property_report_email').id
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)
        notification = {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                                    'title': _('Email Send'),
                                    'type': 'success',
                                    'message': 'Your Email has been sent',
                                    'sticky': False,
                                    }
                        }
        return notification       
        
        
    #send whatsapp Massage
    def action_send_report_whatsapp(self):
        message = 'Hi %s, you property : %s is created , Thank you' % (self.salesmen.name, self.name)
        whatsapp_api_url = 'https://api.whatsapp.com/send?phone=%s&text=%s' % (self.phone, message)
        return{
            'type':'ir.actions.act_url',
            'target':'new',
            'url': whatsapp_api_url
        }
    

    # set garden area and orientation onchange garden
    @api.onchange('garden')
    def change_fields(self):
        for rec in self:
            if rec.garden == True:
                rec.garden_area = 10
                rec.garden_orientation = 'north'
            elif rec.garden == False:
                rec.garden_area = 0
                rec.garden_orientation = ''


    # count total area according gardan area and living area
    @api.depends('living_area', 'garden_area')
    def _total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area


    # action for delete property
    @api.ondelete(at_uninstall=False)
    def error_on_delete(self):
        for rec in self:
            if rec.state == 'new':
                pass  
            elif rec.state == 'offer_received':
                raise exceptions.UserError(
                    ("Offer's in ur property can not delete property!")
                )
            elif rec.state == 'offer_accepted':
                raise exceptions.UserError(
                    ("You Already Accept this property!")
                )
            elif rec.state == 'sold':
                raise exceptions.UserError(
                    ("Property already Sold!..")
                )
            else:
                raise exceptions.UserError(
                    ("You can not delete canceled property!")
                )
            
                                
    # Send mail when property create
    @api.model
    def create(self, vals):
        property = super(RealEstate, self).create(vals)
                                                                              
        template_id = self.env.ref('real_estate_bs.property_created_email').id
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(property.id, force_send=True)

        return property


