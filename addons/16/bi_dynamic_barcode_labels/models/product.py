from odoo import api, fields, models, _
from datetime import datetime
import logging
import json

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    # product_barcode_ids = fields.One2many(
    #     'product.barcode',
    #     'product_tmpl_id',
    #     string='Multi Barcode')
    