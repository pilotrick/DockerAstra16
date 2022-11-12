from odoo import models, fields, api
from odoo.exceptions import Warning

class SaleAdvancePaymentInvLine(models.TransientModel):

    _name = 'sale.advance.payment.inv.line'
    _description = 'Sales Advance Payment Invoice Line'

    advance_payment_wizard_id = fields.Many2one('sale.advance.payment.inv',string='Down Payment')
    sale_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    product_id = fields.Many2one('product.product', string='Product', related='sale_line_id.product_id')
    name = fields.Text(string='Description', related='sale_line_id.name')
    product_uom_qty = fields.Float(string='Quantity', related='sale_line_id.product_uom_qty')
    price_unit = fields.Float(string='Unit Price', related='sale_line_id.price_unit')
    tax_id = fields.Many2many('account.tax', string='Taxes', related='sale_line_id.tax_id')
    currency_id = fields.Many2one(related='sale_line_id.currency_id')
    price_subtotal = fields.Monetary(string='Subtotal', related='sale_line_id.price_subtotal')
    price_tax = fields.Float(related='sale_line_id.price_tax', string='Total Tax')
    price_total = fields.Monetary(related='sale_line_id.price_total', string='Total')

    # Down Payment Related fields
    dp_subtotal = fields.Monetary(string="Dp Subtotal")
    dp_tax_amount = fields.Monetary(string="Dp Taxes")
    dp_total = fields.Monetary(string="Dp Total")