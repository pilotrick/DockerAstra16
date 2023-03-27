from odoo import api, models, fields

class Banks(models.Model):
    _name = 'astra.api.banks'
    
    name = fields.Char('Name')
    bank_code = fields.Char('Bank Code')
    