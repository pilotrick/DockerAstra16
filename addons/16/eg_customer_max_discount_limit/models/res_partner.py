from odoo import models,fields, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    max_discount = fields.Float(string='Descuento Maximo')


