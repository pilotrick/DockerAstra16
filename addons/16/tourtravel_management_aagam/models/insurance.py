# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class InsuranceInsurance(models.Model):
    _name = 'insurance.insurance'
    _description = 'Insurance'
    
    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    adult_cost = fields.Float(string='Adults Cost')
    children_cost = fields.Float(string='Childrens Cost')
    
    