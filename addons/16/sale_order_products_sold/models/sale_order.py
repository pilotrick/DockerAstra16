from odoo import models, fields, api
from datetime import datetime, timedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    products_sold = fields.One2many('sale.order.products.sold', 'order_id', string='Products Sold')
    start_date = fields.Date(string='Fecha de inicio', default=lambda self: datetime.now() - timedelta(days=30))

    @api.onchange('partner_id', 'start_date')
    def _onchange_partner_id(self):
      if self.partner_id and self.start_date:
        partner_id = self.partner_id
        domain = [
          ('partner_id', '=', partner_id.id),
          ('invoice_date', '>=', self.start_date),
          ('invoice_date', '<=', fields.Date.today())
        ]
        invoices = self.env['account.move'].search(domain)
        invoice_order_lines = []
        for invoice in invoices:
          order_line = self.env['sale.order.line'].search([('order_id', '=', invoice.invoice_origin)])
          invoice_order_lines.append(order_line)

        products = []
        for line in invoices.invoice_line_ids:
          product = {
              'product_name': line.product_id.name,
              'quantity': line.quantity,
              'date': line.move_id.invoice_date,
              'price': line.price_unit,
          }
          products.append((0, 0, product))

        self.products_sold = products

class SaleOrderProductsSold(models.Model):
    _name = 'sale.order.products.sold'
    _description = 'Products Sold'

    product_name = fields.Char(string='Product Name')
    quantity = fields.Float(string='Quantity')
    date = fields.Date(string='Date')
    price = fields.Float(string='Price')
    order_id = fields.Many2one('sale.order', string='Sale Order')

    @api.model
    def _init_groups(self):
        group_int_user = self.env.ref('base.group_user')
        group_int_user.write({'implied_ids': [(4, self.env.ref('base.group_internal_user').id)]})
