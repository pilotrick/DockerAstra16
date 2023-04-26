from odoo import api, fields, models


class PropertyType(models.Model):
    _name = 'property.type'

    name = fields.Char(string='Property Type')
    offer_count = fields.Char(string='Offer Count', compute='count_offers')
    
    house = fields.One2many(
        'real.estate', 'property_type_id', string='house')
    offer_ids = fields.One2many(
        'property.offer', 'property_id', string='Offer Id')
                                
    # sql constraints
    _sql_constraints = [
        ( 'unique_type', 'unique(name)', 'Type Must Be Unique.' )
    ]

    # count all offers for same property type
    @api.depends('offer_ids')
    def count_offers(self):
        for rec in self:
            rec.offer_count = len(rec.house.new_offers)

    # show all property offers for same property type view
    def get_offers(self):
        for rec in self:
            return {
                'name' : 'Offers',
                'view_mode': 'tree',
                'res_model' : 'property.offer',
                'view_id' : self.env.ref('real_estate_bs.property_offer_list_view').id ,
                'domain' : [('id' , 'in' ,rec.house.new_offers.ids)],
                'type' : 'ir.actions.act_window'
                    }   
            