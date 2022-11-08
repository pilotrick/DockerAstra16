from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class SaleAdvancePaymentInv(models.TransientModel):

    _inherit = 'sale.advance.payment.inv'

    lines = fields.One2many('sale.advance.payment.inv.line', 'advance_payment_wizard_id', string="Lines")

    @api.onchange('amount', 'fixed_amount')
    def onchange_amount(self):
        self.ensure_one()
        self.sudo().write({'lines':False})
        dp_line = self.env['sale.advance.payment.inv.line']
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        if sale_orders:
            sale_order = sale_orders[0]
            for line in sale_order.order_line.filtered(lambda x : not x.is_downpayment and x.display_type not in ["line_section", "line_note"]):
                if self.advance_payment_method == 'percentage':
                    dp_amount = line.price_subtotal * self.amount / 100
                    taxes = line.tax_id.compute_all(dp_amount, line.order_id.currency_id)
                    dp_line.create({
                        'advance_payment_wizard_id': self.id,
                        'sale_line_id': line.id,
                        'dp_subtotal': taxes['total_excluded'],
                        'dp_tax_amount': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                        'dp_total': taxes['total_included'],
                    })
                if self.advance_payment_method == 'fixed':
                    dp_amount = line.price_subtotal * self.fixed_amount / sale_order.amount_total
                    if line.tax_id and line.tax_id[0].price_include:
                        dp_amount = line.price_subtotal * self.fixed_amount / sale_order.amount_untaxed
                    taxes = line.tax_id.compute_all(dp_amount, line.order_id.currency_id)
                    dp_line.create({
                        'advance_payment_wizard_id': self.id,
                        'sale_line_id': line.id,
                        'dp_subtotal': taxes['total_excluded'],
                        'dp_tax_amount': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                        'dp_total': taxes['total_included'],
                    })
        self.flush()

    def _prepare_invoice_values(self, order, name, amount, so_line, mapping=None):
        res = super(SaleAdvancePaymentInv,self)._prepare_invoice_values(order, name, amount, so_line)
        invoice_lines = []
        for line in self.lines:
            #so_line = mapping.get(line)
            subtotal = line.dp_subtotal
            if line.tax_id and line.tax_id[0].price_include:
                subtotal = line.dp_total
            new_line = (0, 0, {
                'name': line.name,
                'price_unit': subtotal,
                'quantity': 1.0,
                'product_id': self.product_id.id,
                'product_uom_id': so_line.product_uom.id,
                'tax_ids': [(6, 0, line.tax_id.ids)],
                'sale_line_ids': [(6, 0, [so_line.id])],
                'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                'analytic_account_id': order.analytic_account_id.id or False,
            })
            invoice_lines.append(new_line)
        if invoice_lines:
            res['invoice_line_ids'] = invoice_lines
        return res

    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        if len(sale_orders) == 1:
            if self.advance_payment_method == 'delivered':
                sale_orders._create_invoices(final=self.deduct_down_payments)
            else:
                # Create deposit product if necessary
                if not self.product_id:
                    vals = self._prepare_deposit_product()
                    self.product_id = self.env['product.product'].create(vals)
                    self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)

                sale_line_obj = self.env['sale.order.line']
                for order in sale_orders:
                    amount, name = self._get_advance_details(order)

                    if self.product_id.invoice_policy != 'order':
                        raise UserError(_('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
                    if self.product_id.type != 'service':
                        raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
                    taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
                    tax_ids = order.fiscal_position_id.map_tax(taxes).ids   
                    analytic_tag_ids = []
                    for line in order.order_line:
                        analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]

                    mapping = {}
                    for line in self.lines:
                        taxes = line.tax_id
                        tax_ids = order.fiscal_position_id.map_tax(taxes).ids
                        so_line_values = self._prepare_so_line(order, analytic_tag_ids, tax_ids, line.dp_subtotal)
                        so_line = sale_line_obj.create(so_line_values)
                        mapping[line] = so_line

                    self._create_invoice(order, so_line, line.dp_subtotal)

                        
                    #self._create_invoice(order, so_line, amount, mapping=mapping)
            if self._context.get('open_invoices', False):
                return sale_orders.action_view_invoice()
            return {'type': 'ir.actions.act_window_close'}
        else:
            return super(SaleAdvancePaymentInv,self).create_invoices()
        

    def _create_invoice(self, order, so_line, amount, mapping=None):
        if (self.advance_payment_method == 'percentage' and self.amount <= 0.00) or (self.advance_payment_method == 'fixed' and self.fixed_amount <= 0.00):
            raise UserError(_('The value of the down payment amount must be positive.'))

        amount, name = self._get_advance_details(order)

        invoice_vals = self._prepare_invoice_values(order, name, amount, so_line, mapping)

        if order.fiscal_position_id:
            invoice_vals['fiscal_position_id'] = order.fiscal_position_id.id
        invoice = self.env['account.move'].sudo().create(invoice_vals).with_user(self.env.uid)
        invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': invoice, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return invoice