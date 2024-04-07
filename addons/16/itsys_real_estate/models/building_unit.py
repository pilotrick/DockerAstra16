# -*- coding: utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.addons.web_editor.tools import get_video_embed_code

class building_unit(models.Model):
    _inherit = ['product.template']
    _description = "Property"

    def view_reservations(self):
        reservation_obj = self.env['unit.reservation']
        reservations_ids = reservation_obj.search([('building_unit', '=', self.ids)])
        reservations=[]
        for obj in reservations_ids: reservations.append(obj.id)
        return {
            'name': _('Reservation'),
            'domain': [('id', 'in', reservations)],
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model':'unit.reservation',
            'type':'ir.actions.act_window',
            'nodestroy':True,
            'view_id': False,
            'target':'current',
        }

    def _reservation_count(self):
        reservation_obj = self.env['unit.reservation']
        for unit in self:
            reservations_ids = reservation_obj.search([('building_unit', '=', unit.id)])    
            unit.reservation_count = len(reservations_ids)

    attach_line= fields.One2many("unit.attachment.line", "product_attach_id", "Documents")
    video_url= fields.Char ('Vidoe URL')
    url= fields.Char ('Website URL')
    website_published= fields.Boolean ('Website Published',default=True)
    lng= fields.Float   ('Longitude')
    lat= fields.Float   ('Latitude')
    is_property= fields.Boolean ('Property')
    contacts= fields.Many2many('res.partner',string='Contacts')
    building_id= fields.Many2one('building','Building')
    region_id= fields.Many2one('regions', string='Region', related='building_id.region_id', store=True, readonly=True)
    component_ids= fields.One2many('components.line', 'unit_id', string='Components List')
    reservation_count= fields.Integer(compute='_reservation_count',string='Reservation Count',)        
    cnt= fields.Integer   ('Count',default=1)
    unit_status2= fields.Char    ('Status', size=16)
    active= fields.Boolean ('Active', help="If the active field is set to False, it will allow you to hide the top without removing it.",default=True)
    alarm= fields.Boolean ('Alarm')
    old_building= fields.Boolean ('Old Building')
    constructed= fields.Date ('Construction Date')
    category= fields.Char    ('Category', size=16)
    description= fields.Text    ('Description')
    floor= fields.Char    ('Floor', size=16)
    pricing= fields.Integer   ('Selling Price',compute='_calc_price',store=True)
    balcony= fields.Integer   ('Balconies m²',)
    building_area= fields.Integer   ('Building Unit Area m²',)
    building_area_net= fields.Integer   ('Net Area m²',compute='_calc_building_area_net',store=True)
    price_per_m = fields.Float('Price Per m²', )
    price_before_discount = fields.Float('Price', compute='_calc_price', store=True)
    discount_type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')])
    discount = fields.Float('Dsicount')

    land_area= fields.Integer   ('Gross Area m²',)
    land_ratio= fields.Float   ('Load Ratio',)

    @api.depends('land_area', 'land_ratio')
    def _calc_building_area_net(self):
        for rec in self:
            if rec.land_ratio:
                rec.building_area_net = rec.land_area - rec.land_ratio

    garden= fields.Integer   ('Garden m²',)
    terrace= fields.Integer   ('Terraces m²',)
    garage= fields.Integer ('Garage included')
    carport= fields.Integer ('Carport included')
    parking_place_rentable= fields.Boolean ('Parking rentable', help="Parking rentable in the location if available")
    handicap= fields.Boolean ('Handicap Accessible')
    heating= fields.Selection([('unknown','unknown'),
                                          ('none','none'),
                                           ('tiled_stove', 'tiled stove'),
                                           ('stove', 'stove'),
                                           ('central','central heating'),
                                           ('self_contained_central','self-contained central heating')], 'Heating',)
    heating_source= fields.Selection([('unknown','unknown'),
                                           ('electricity','Electricity'),
                                           ('wood','Wood'),
                                           ('pellets','Pellets'),
                                           ('oil','Oil'),
                                           ('gas','Gas'),
                                           ('district','District Heating')], 'Heating Source')
    internet= fields.Boolean ('Internet')
    lease_target= fields.Integer   ('Target Lease', )
    lift= fields.Integer ('# Passenger Elevators')
    lift_f= fields.Integer ('# Freight Elevators')
    name= fields.Char    ('Name',  required=True)
    code= fields.Char    ('Code', size=16)
    note= fields.Html    ('Notes')
    note_sales= fields.Text    ('Note Sales Folder')
    partner_id= fields.Many2one('res.partner','Owner')
    ptype= fields.Many2one('building.type','Building Unit Type')

    @api.onchange('ptype')
    def onchange_ptype(self):
        self.land_ratio = self.ptype.land_ratio

    status= fields.Many2one('building.status','Unit Status')
    desc= fields.Many2one('building.desc','Description')
    partner_from= fields.Date    ('Purchase Date')
    partner_to= fields.Date    ('Sale Date')
    rooms= fields.Integer    ('# Rooms')
    bathrooms= fields.Integer    ('# Bathrooms')
    solar_electric= fields.Boolean ('Solar Electric System')
    solar_heating= fields.Boolean ('Solar Heating System')
    staircase= fields.Char    ('Staircase', size=8)
    surface= fields.Integer   ('Surface', )
    telephon= fields.Boolean ('Telephon')
    tv_cable= fields.Boolean ('Cable TV')
    tv_sat= fields.Boolean ('SAT TV')
    usage= fields.Selection([('unlimited','unlimited'),
                                          ('office','Office'),
                                           ('shop','Shop'),
                                           ('flat','Flat'),
                                            ('rural','Rural Property'),
                                           ('parking','Parking')], 'Usage')
    sort= fields.Integer ('Sort')
    sequence= fields.Integer ('Sequ.')
    air_condition= fields.Selection([('unknown','Unknown'),
                                           ('central','Central'),
                                           ('partial','Partial'),
                                           ('none', 'None'),
                                           ], 'Air Condition' )
    address= fields.Char    ('Address')
    license_code= fields.Char    ('License Code', size=16)
    license_date= fields.Date    ('License Date')
    date_added= fields.Date    ('Date Added to Notarization')
    license_location= fields.Char    ('License Notarization')
    electricity_meter= fields.Char    ('Electricity meter', size=16)
    water_meter= fields.Char    ('Water meter', size=16)
    north= fields.Char    ('Northen border by:')
    south= fields.Char    ('Southern border by:')
    east= fields.Char    ('Eastern border  by:')
    west= fields.Char    ('Western border by:')
    rental_fee= fields.Integer   ('Rental fee')
    insurance_fee= fields.Integer   ('Insurance fee')
    template_id= fields.Many2one('installment.template','Payment Template')
    state= fields.Selection([('free','Available'),
                               ('reserved','Booked'),
                               ('on_lease','Leased'),
                               ('sold','Sold'),
                               ('blocked','Blocked'),
                               ], 'State',default='free' )
    property_template_image_ids = fields.One2many('property.image', 'product_tmpl_id', string="Extra Product Media", copy=True)
    street = fields.Char(related='region_id.street', store=True)
    street2 = fields.Char(related='region_id.street2', store=True)
    zip = fields.Char(related='region_id.zip', store=True)
    city = fields.Char(related='region_id.city', store=True)
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               related='region_id.state_id', store=True)
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', related='region_id.country_id',
                                 store=True)
    country_code = fields.Char(related='country_id.code', string="Country Code",
  store = True)

    @api.depends('price_per_m', 'discount_type', 'discount', 'land_area')
    def _calc_price(self):
        for rec in self:
            rec.price_before_discount = rec.price_per_m * rec.land_area
            if rec.discount_type == 'amount':
                rec.pricing = rec.price_before_discount - rec.discount
            elif rec.discount_type == 'percentage':
                rec.pricing = rec.price_before_discount - ((rec.discount / 100) * rec.price_before_discount)
            else:
                rec.pricing = rec.price_before_discount

    _sql_constraints = [
        ('unique_property_code', 'UNIQUE (code,building_id,region_id)', 'property code must be unique!'),
        ('unique_property_building_code', 'UNIQUE (code,building_id)', 'property code must be unique!'),
    ]

    def make_reservation(self):
        for unit_obj in self:
            code =  unit_obj.code
            building_unit =  unit_obj.id
            address =  unit_obj.address
            floor =  unit_obj.floor
            pricing =  unit_obj.pricing
            type =  unit_obj.ptype.id
            status =  unit_obj.status.id
            building =  unit_obj.building_id.id
            building_code =  unit_obj.building_id.code
            region =  unit_obj.region_id.id
            building_area =  unit_obj.building_area
            
        vals= {'region':region,'building_code':building_code,
               'building':building,'unit_code': code,'floor': floor,'pricing': pricing,
               'type': type,'address': address,'status': status,
               'building_area': building_area,'building_unit':building_unit}

        reservation_obj = self.env['unit.reservation']        
        reservation_id = reservation_obj.create(vals)
        return {
            'view_type':'form',
            'view_mode':'form',
            'res_model':'unit.reservation',
            'type':'ir.actions.act_window',
            'nodestroy':True,
            'target':'current',
            'res_id': reservation_id.id,
        }


class components_line(models.Model):
    _name = "components.line"    
    component= fields.Many2one('component','Components', required=True)
    unit_id= fields.Many2one('product.template', 'Building Unit View',domain=[('is_property', '=', True)])
    

class component(models.Model):
    _name = "component"
    name= fields.Char('Name', required=True)
    qty= fields.Integer('Quantity', required=True)
    furniture_details_ids= fields.One2many('furniture', 'component_id', string='Furniture List')

class furniture(models.Model):
    _name = "furniture"    
    product_id= fields.Many2one('product.product','Furniture',required=True)
    component_id= fields.Many2one('component', 'Component View')

class product_template(models.Model):
    _inherit = "product.template"
    furniture= fields.Boolean('Furniture')

class FloorPlans(models.Model):
    _name = 'floor.plans'
    _description = "Floor Plans"
    _inherit = ['image.mixin']
    _order = 'sequence, id'

    name = fields.Char("Name", required=True)
    sequence = fields.Integer(default=10, index=True)
    image_1920 = fields.Image(required=True)
    product_tmpl_id = fields.Many2one('product.template', "Product Template", index=True, ondelete='cascade')
    product_variant_id = fields.Many2one('product.product', "Product Variant", index=True, ondelete='cascade')
    video_url = fields.Char('Video URL',
                            help='URL of a video for showcasing your property.')
    embed_code = fields.Char(compute="_compute_embed_code")
    can_image_1024_be_zoomed = fields.Boolean("Can Image 1024 be zoomed", compute='_compute_can_image_1024_be_zoomed', store=True)

    @api.depends('image_1920', 'image_1024')
    def _compute_can_image_1024_be_zoomed(self):
        for image in self:
            image.can_image_1024_be_zoomed = image.image_1920 and tools.is_image_size_above(image.image_1920, image.image_1024)

    @api.depends('video_url')
    def _compute_embed_code(self):
        for image in self:
            image.embed_code = get_video_embed_code(image.video_url)

    @api.constrains('video_url')
    def _check_valid_video_url(self):
        for image in self:
            if image.video_url and not image.embed_code:
                raise ValidationError(_("Provided video URL for '%s' is not valid. Please enter a valid video URL.", image.name))

    @api.model_create_multi
    def create(self, vals_list):
        """
            We don't want the default_product_tmpl_id from the context
            to be applied if we have a product_variant_id set to avoid
            having the variant images to show also as template images.
            But we want it if we don't have a product_variant_id set.
        """
        context_without_template = self.with_context({k: v for k, v in self.env.context.items() if k != 'default_product_tmpl_id'})
        normal_vals = []
        variant_vals_list = []

        for vals in vals_list:
            if vals.get('product_variant_id') and 'default_product_tmpl_id' in self.env.context:
                variant_vals_list.append(vals)
            else:
                normal_vals.append(vals)

        return super().create(normal_vals) + super(FloorPlans, context_without_template).create(variant_vals_list)


class unit_attachment_line(models.Model):
    _name = 'unit.attachment.line'

    name= fields.Char    ('Name', required=True)
    file= fields.Binary    ('File',)
    product_attach_id= fields.Many2one('product.template', '',ondelete='cascade', readonly=True)

