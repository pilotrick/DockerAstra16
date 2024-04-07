# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, get_lang


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    apply_manual_currency_exchange = fields.Boolean(
        string='Apply Manual Currency Exchange')
    manual_currency_exchange_rate = fields.Float(string='Manual Currency Exchange Rate')
    active_manual_currency_rate = fields.Boolean(
        'active Manual Currency', default=False)

    def _prepare_invoice(self):
        result = super(PurchaseOrder, self)._prepare_invoice()
        result.update({
            'apply_manual_currency_exchange': self.apply_manual_currency_exchange,
            'manual_currency_exchange_rate': self.manual_currency_exchange_rate,
        })
        return result

    @api.onchange('company_id', 'currency_id')
    def onchange_currency_id(self):
        if self.company_id or self.currency_id:
            if self.company_id.currency_id != self.currency_id:
                self.active_manual_currency_rate = True
            else:
                self.active_manual_currency_rate = False
        else:
            self.active_manual_currency_rate = False

    def _prepare_invoice(self):
        res = super(PurchaseOrder, self)._prepare_invoice()
        res.update({
            'apply_manual_currency_exchange': self.apply_manual_currency_exchange,
            'manual_currency_exchange_rate': self.manual_currency_exchange_rate,
            'active_manual_currency_rate': self.active_manual_currency_rate
        })
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('product_qty', 'product_uom', 'order_id.apply_manual_currency_exchange', 'order_id.manual_currency_exchange_rate')
    def _compute_price_unit_and_date_planned_and_name(self):
        for line in self:
            if not line.product_id or line.invoice_lines:
                continue
            params = {'order_id': line.order_id}
            seller = line.product_id._select_seller(
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order and line.order_id.date_order.date(),
                uom_id=line.product_uom,
                params=params)

            manual_currency_rate_active = line.order_id.apply_manual_currency_exchange
            manual_currency_rate = line.order_id.manual_currency_exchange_rate

            if seller or not line.date_planned:
                line.date_planned = line._get_date_planned(
                    seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

            # If not seller, use the standard price. It needs a proper currency conversion.
            if not seller:
                unavailable_seller = line.product_id.seller_ids.filtered(
                    lambda s: s.partner_id == line.order_id.partner_id)

                if not unavailable_seller and line.price_unit and line.product_uom == line._origin.product_uom and not manual_currency_rate_active:
                    # Avoid to modify the price unit if there is no price list for this partner and
                    # the line has already one to avoid to override unit price set manually.
                    continue
                po_line_uom = line.product_uom or line.product_id.uom_po_id
                price_unit = line.env['account.tax']._fix_tax_included_price_company(
                    line.product_id.uom_id._compute_price(
                        line.product_id.standard_price, po_line_uom),
                    line.product_id.supplier_taxes_id,
                    line.taxes_id,
                    line.company_id,
                )

                if manual_currency_rate_active and manual_currency_rate > 0:
                    line.price_unit = price_unit / manual_currency_rate
                else:
                    line.price_unit = line.currency_id._convert(
                        price_unit,
                        line.currency_id,
                        line.company_id,
                        line.date_order,
                    )
                continue

            price_unit = line.env['account.tax']._fix_tax_included_price_company(
                seller.price, line.product_id.supplier_taxes_id, line.taxes_id, line.company_id) if seller else 0.0

            if manual_currency_rate_active:
                price_unit = price_unit / manual_currency_rate
            else:
                price_unit = seller.currency_id._convert(
                    price_unit, line.currency_id, line.company_id, line.date_order)

            line.price_unit = seller.product_uom._compute_price(
                price_unit, line.product_uom)

            # record product names to avoid resetting custom descriptions
            default_names = []
            vendors = line.product_id._prepare_sellers({})
            for vendor in vendors:
                product_ctx = {'seller_id': vendor.id, 'lang': get_lang(
                    line.env, line.partner_id.lang).code}
                default_names.append(line._get_product_purchase_description(
                    line.product_id.with_context(product_ctx)))
            if not line.name or line.name in default_names:
                product_ctx = {'seller_id': seller.id, 'lang': get_lang(
                    line.env, line.partner_id.lang).code}
                line.name = line._get_product_purchase_description(
                    line.product_id.with_context(product_ctx))
