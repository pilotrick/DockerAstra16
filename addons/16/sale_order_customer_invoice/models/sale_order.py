from odoo import models, fields, api
from datetime import datetime, timedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoice_template = fields.One2many('sale.order.invoice.template', 'order_id', string='Customer Invoice')

    @api.onchange('partner_id')
    def _onchange_partner_id_show_customer_invoice(self):
      if self.partner_id:
        partner_id = self.partner_id
        domain = [
          ('partner_id', '=', partner_id.id),
          ('payment_state', 'not in', ['paid']),
          ('state', 'in', ['posted']),
          ('move_type', 'in', ['out_invoice', 'out_refund'])
        ]

        invoices = self.env['account.move'].search(domain)
        self.invoice_template = False

        invoice_list = []
        for invoice in invoices:
          invoice_template = {
              'partner_id': invoice.partner_id.id or False,
              'invoice_date': invoice.invoice_date or None,
              'invoice_date_due': invoice.invoice_date_due or None,
              'state': invoice.state or False,
              'payment_state': invoice.payment_state or False,
              'reference': invoice.name or '',
              'credit_payment': invoice.credit_payment or 0.0,
              'balance_due_amount': invoice.balance_due_amount or 0.0,
              'amount_total': invoice.amount_total or 0.0,
              'transaction_ids': invoice.transaction_ids.ids or [],
              'move_type': invoice.move_type or False,
              'invoice_id': invoice.id,
              'company_id': invoice.company_id or self.env.user.company_id
          }
          invoice_list.append((0, 0, invoice_template))

        self.invoice_template = invoice_list

class SaleOrderInvoiceTemplate(models.Model):
    _name = 'sale.order.invoice.template'
    _description = 'Invoice Template'

    invoice_id = fields.Integer(string='Invoice Id')
    partner_id = fields.Char(string='Customer')
    order_id = fields.Many2one('sale.order', string='Sale Order')
    #name = fields.Char(string='Number')
    state = fields.Selection(
      selection=[
          ('draft', 'Draft'),
          ('posted', 'Posted'),
          ('cancel', 'Cancelled'),
      ],
      string='Status',
      required=True,
      default='draft',
    )
    invoice_date = fields.Date(string='Invoice/Bill Date')
    invoice_date_due = fields.Date(string='Due Date')
    payment_state = fields.Selection(
        selection=[
            ('not_paid', 'Not Paid'),
            ('in_payment', 'In Payment'),
            ('paid', 'Paid'),
            ('partial', 'Partially Paid'),
            ('reversed', 'Reversed'),
            ('invoicing_legacy', 'Invoicing App Legacy'),
        ],
        string="Payment Status",
        compute='_compute_payment_state'
    )
    reference = fields.Char(string='Reference')
    credit_payment = fields.Float(string='Credit Amount')
    balance_due_amount = fields.Float(string='Balance Due Amount')
    amount_total = fields.Float(string='Amount Total')
    transaction_ids = fields.Many2many(string='Transactions')
    move_type = fields.Selection(
        selection=[
            ('entry', 'Journal Entry'),
            ('out_invoice', 'Customer Invoice'),
            ('out_refund', 'Customer Credit Note'),
            ('in_invoice', 'Vendor Bill'),
            ('in_refund', 'Vendor Credit Note'),
            ('out_receipt', 'Sales Receipt'),
            ('in_receipt', 'Purchase Receipt'),
        ],
        string='Type',
        default="entry",
    )
    company_id = fields.Many2one(
      comodel_name='res.company',
      string='Company'
    )