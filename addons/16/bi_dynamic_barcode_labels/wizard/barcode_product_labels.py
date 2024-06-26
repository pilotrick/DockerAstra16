# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BarcodeProductLabelsWiz(models.TransientModel):
    _name = "barcode.product.labels.wiz"
    _description = 'Barcode Product Labels Wizard'

    product_barcode_ids = fields.One2many('barcode.product.labels.wiz.line', 'label_id', 'Product Barcode')

    @api.model
    def default_get(self, fields):
        res = super(BarcodeProductLabelsWiz, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        product_ids = self.env['product.product'].browse(active_ids)
        barcode_lines = []
        for product in product_ids:
            barcode_lines.append((0,0, {
                'label_id' : self.id,
                'product_id' : product.id, 
                'qty' : 1,
            }))
        res.update({
            'product_barcode_ids': barcode_lines
        })
        return res


    def print_barcode_labels_zebra(self):
        pass
        # self.ensure_one()
        # [data] = self.read()
        # barcode_config = self.env.ref('bi_dynamic_barcode_labels.barcode_labels_config_data')
        # if not barcode_config.barcode_currency_id or not barcode_config.barcode_currency_position:
        #     raise UserError(_('Barcode Configuration fields are not set in data (Inventory -> Settings -> Barcode Configuration)'))
        # data['barcode_labels'] = data['product_barcode_ids']
        # barcode_lines = self.env['barcode.product.labels.wiz.line'].browse(data['barcode_labels'])
        # datas = {
        #      'ids': [1],
        #      'model': 'barcode.product.labels.wiz',
        #      'form': data
        # }
        # return self.env.ref('bi_dynamic_barcode_labels.printed_barcode_labels_id').report_action(barcode_lines, data=datas)

    def print_barcode_labels(self):
        pass

class BarcodeProductLabelsLine(models.TransientModel):
    _name = "barcode.product.labels.wiz.line"
    _description = 'Barcode Product Labels Line'
    
    label_id = fields.Many2one('barcode.product.labels.wiz', 'Barcode labels')
    product_id = fields.Many2one('product.product', 'Product')
    qty = fields.Integer('Barcode', default=1)
    company_id = fields.Many2one('res.company','Company', default=lambda self: self.env.company)