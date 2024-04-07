# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    product_image = fields.Binary(related='product_id.image_1920')
    warehouse = fields.Many2one(comodel_name='stock.warehouse',string="Warehouse",related='move_id.warehouse_id')
    seller = fields.Many2one(comodel_name='res.users',string='Vendedor',related='move_id.invoice_user_id', readonly=True)
    margin_amount = fields.Char(string='margen',related='move_id.margin_amount')
    margin_percentage = fields.Char(String="Margen(%)", related='move_id.margin_percentage')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Clinte')
    origin_document = fields.Char(string='Documento de Origen', related='move_id.invoice_origin')
    cost = fields.Float (string="Costo", related='product_id.standard_price')
    product_category = fields.Many2one (string="Categoria de producto", related='product_id.categ_id')
    payment_status = fields.Selection([('not_paid','No pagadas'),('in_payment','En proceso de pago'),('paid','Pagado'),('partial','Pagado Parcialmente'),('reversed','Revertido'),('invoicing_legacy','Factura Sistema Anterior')], string="Estado de pago", related='move_id.payment_state')
    amount_total_signed = fields.Monetary(string="Total", related='move_id.amount_total_signed')
    
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id, store=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True, store=True)
    
    