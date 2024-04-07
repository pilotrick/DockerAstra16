# coding: utf-8
from odoo import _, api, fields, models
from odoo.tools.misc import get_lang


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        ''' While validating the sales order that does not have online payment and
         product invoice policy based on ordered quantity it will create invoice and
         confirm the invoice also send the mail. '''
        res = super(SaleOrder, self).action_confirm()
        if not self.require_payment and not self.order_line.filtered(
                lambda l: l.product_id.invoice_policy == 'delivery'):
            advance_payment = self.env['sale.advance.payment.inv'].with_context(
                active_ids=self.ids, open_invoices=True).create({'advance_payment_method': 'delivered',
                                                                 })
            inv = advance_payment.create_invoices()
            invoice = self.env['account.move'].browse(int(inv.get('res_id')))
            invoice.action_post()
            template = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
            lang = False
            if template:
                lang = template._render_lang(invoice.ids)[invoice.id]
            if not lang:
                lang = get_lang(self.env).code
            ctx = dict(
                default_model='account.move',
                default_res_id=invoice.id,
                default_res_model='account.move',
                default_use_template=bool(template),
                default_template_id=template and template.id or False,
                default_composition_mode='comment',
                mark_invoice_as_sent=True,
                custom_layout="mail.mail_notification_paynow",
                model_description=self.with_context(lang=lang).type_name,
                force_email=True,
                active_ids=invoice.ids
            )

            invoice_send = self.env['account.invoice.send'].with_context(ctx).create({
                'is_print': False,
                'partner_ids': invoice.partner_id.ids
            })
            invoice_send.onchange_template_id()
            invoice_send.send_and_print_action()

        return res
