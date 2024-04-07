# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.tools.float_utils import float_round, float_is_zero
from odoo.exceptions import UserError


class stock_move(models.Model):
    _inherit = 'stock.move'

    def _get_price_unit(self):
        """ Returns the unit price for the move"""
        self.ensure_one()
        if self.purchase_line_id and self.product_id.id == self.purchase_line_id.product_id.id:
            price_unit_prec = self.env['decimal.precision'].precision_get(
                'Product Price')
            line = self.purchase_line_id
            order = line.order_id
            price_unit = line.price_unit
            if line.taxes_id:
                qty = line.product_qty or 1
                price_unit = line.taxes_id.with_context(round=False).compute_all(
                    price_unit, currency=line.order_id.currency_id, quantity=qty)['total_void']
                price_unit = float_round(
                    price_unit / qty, precision_digits=price_unit_prec)
            if line.product_uom.id != line.product_id.uom_id.id:
                price_unit *= line.product_uom.factor / line.product_id.uom_id.factor

            if order.currency_id != order.company_id.currency_id:
                if order.apply_manual_currency_exchange:
                    price_unit = price_unit * order.manual_currency_exchange_rate
                    # The date must be today, and not the date of the move since the move move is still
                    # in assigned state. However, the move date is the scheduled date until move is
                    # done, then date of actual move processing. See:
                    # https://github.com/odoo/odoo/blob/2f789b6863407e63f90b3a2d4cc3be09815f7002/addons/stock/models/stock_move.py#L36
                else:
                    price_unit = order.currency_id._convert(
                        price_unit, order.company_id.currency_id, order.company_id, fields.Date.context_today(self), round=False)
            return price_unit
        return super(stock_move, self)._get_price_unit()

    def _get_in_svl_vals(self, forced_quantity):
        """Create a `stock.valuation.layer` from `self`.

        :param forced_quantity: under some circunstances, the quantity to value is different than
            the initial demand of the move (Default value = None)
        """

        rec = super(stock_move, self)._get_in_svl_vals(forced_quantity)
        for rc in rec:
            for line in self:
                if line.purchase_line_id:
                    if line.purchase_line_id.order_id.apply_manual_currency_exchange:
                        price_unit = line.purchase_line_id.order_id.currency_id.round(
                            (line.purchase_line_id.price_subtotal) * line.purchase_line_id.order_id.manual_currency_exchange_rate)

                        order_quantity = line.purchase_line_id.product_uom._compute_quantity(
                            line.purchase_line_id.product_uom_qty, line.purchase_line_id.product_uom
                        )
                        unit_cost = price_unit / order_quantity
                        rc['unit_cost'] = round(unit_cost, 2)
                        rc['value'] = round(unit_cost * rc['quantity'], 2)
                        rc['remaining_value'] = round(unit_cost * rc['quantity'], 2)
        return rec

    # def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id, description):
    #     """
    #     Generate the account.move.line values to post to track the stock valuation difference due to the
    #     processing of the given quant.
    #     """
    #     self.ensure_one()

    #     # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
    #     # the company currency... so we need to use round() before creating the accounting entries.
    #     debit_value = self.company_id.currency_id.round(cost)
    #     credit_value = debit_value

    #     valuation_partner_id = self._get_partner_id_for_valuation_lines()

    #     if self.purchase_line_id.order_id.apply_manual_currency_exchange:
    #         debit_value = self.purchase_line_id.order_id.currency_id.round(
    #             (self.purchase_line_id.price_unit * qty) * self.purchase_line_id.order_id.manual_currency_exchange_rate)
    #         credit_value = debit_value

    #         res = [(0, 0, line_vals) for line_vals in self._generate_valuation_lines_data(
    #             valuation_partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description).values()]

    #     else:
    #         res = [(0, 0, line_vals) for line_vals in self._generate_valuation_lines_data(
    #             valuation_partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description).values()]

    #     if self.sale_line_id.order_id.sale_manual_currency_rate != 0:
    #         debit_value = self.sale_line_id.order_id.currency_id.round(
    #             (self.sale_line_id.price_unit * qty) * self.sale_line_id.order_id.sale_manual_currency_rate)
    #         credit_value = debit_value
    #         res = [(0, 0, line_vals) for line_vals in self._generate_valuation_lines_data(
    #             valuation_partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description).values()]

    #     else:
    #         res = [(0, 0, line_vals) for line_vals in self._generate_valuation_lines_data(
    #             valuation_partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description).values()]

    #     return res

    # def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description):
    #     # This method returns a dictionary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
    #     raise Warning("JODERRRRRRRRR")
    #     company_currency = self.company_id.currency_id

    #     diff_currency_po = self.purchase_line_id.order_id.currency_id != company_currency
    #     diff_currency_so = self.sale_line_id.order_id.currency_id != company_currency

    #     ctx = dict(self._context, lang=self.purchase_line_id.order_id.partner_id.lang)
    #     self.ensure_one()
    #     if self._context.get('forced_ref'):
    #         ref = self._context['forced_ref']
    #     else:
    #         ref = self.picking_id.name
    #     if self.purchase_line_id:
    #         debit_line_vals = {
    #             'name': self.name,
    #             'product_id': self.product_id.id,
    #             'quantity': qty,
    #             'product_uom_id': self.product_id.uom_id.id,
    #             'ref': ref,
    #             'partner_id': partner_id,
    #             'debit': debit_value if debit_value > 0 else 0,
    #             'credit': -debit_value if debit_value < 0 else 0,
    #             'account_id': debit_account_id,
    #             'amount_currency': diff_currency_po and (self.purchase_line_id.price_unit) * qty,
    #             'currency_id': diff_currency_po and self.purchase_line_id.order_id.currency_id.id,
    #         }

    #         credit_line_vals = {
    #             'name': self.name,
    #             'product_id': self.product_id.id,
    #             'quantity': qty,
    #             'product_uom_id': self.product_id.uom_id.id,
    #             'ref': ref,
    #             'partner_id': partner_id,
    #             'credit': credit_value if credit_value > 0 else 0,
    #             'debit': -credit_value if credit_value < 0 else 0,
    #             'account_id': credit_account_id,
    #             'amount_currency': diff_currency_po and (-self.purchase_line_id.price_unit) * qty,
    #             'currency_id': diff_currency_po and self.purchase_line_id.order_id.currency_id.id,
    #         }
    #     elif self.sale_line_id and self.sale_line_id.order_id.sale_manual_currency_rate_active:
    #         debit_line_vals = {
    #             'name': self.name,
    #             'product_id': self.product_id.id,
    #             'quantity': qty,
    #             'product_uom_id': self.product_id.uom_id.id,
    #             'ref': ref,
    #             'partner_id': partner_id,
    #             'debit': debit_value if debit_value > 0 else 0,
    #             'credit': -debit_value if debit_value < 0 else 0,
    #             'account_id': debit_account_id,
    #             'amount_currency': diff_currency_so and (self.sale_line_id.price_unit) * qty,
    #             'currency_id': diff_currency_so and self.sale_line_id.order_id.currency_id.id,
    #         }

    #         credit_line_vals = {
    #             'name': self.name,
    #             'product_id': self.product_id.id,
    #             'quantity': qty,
    #             'product_uom_id': self.product_id.uom_id.id,
    #             'ref': ref,
    #             'partner_id': partner_id,
    #             'credit': credit_value if credit_value > 0 else 0,
    #             'debit': -credit_value if credit_value < 0 else 0,
    #             'account_id': credit_account_id,
    #             'amount_currency': diff_currency_so and (-self.sale_line_id.price_unit) * qty,
    #             'currency_id': diff_currency_so and self.sale_line_id.order_id.currency_id.id,
    #         }
    #     else:
    #         debit_line_vals = {
    #             'name': self.name,
    #             'product_id': self.product_id.id,
    #             'quantity': qty,
    #             'product_uom_id': self.product_id.uom_id.id,
    #             'ref': ref,
    #             'partner_id': partner_id,
    #             'debit': debit_value if debit_value > 0 else 0,
    #             'credit': -debit_value if debit_value < 0 else 0,
    #             'account_id': debit_account_id,
    #         }

    #         credit_line_vals = {
    #             'name': self.name,
    #             'product_id': self.product_id.id,
    #             'quantity': qty,
    #             'product_uom_id': self.product_id.uom_id.id,
    #             'ref': ref,
    #             'partner_id': partner_id,
    #             'credit': credit_value if credit_value > 0 else 0,
    #             'debit': -credit_value if credit_value < 0 else 0,
    #             'account_id': credit_account_id,
    #         }

    #     rslt = {'credit_line_vals': credit_line_vals,
    #             'debit_line_vals': debit_line_vals}
    #     if credit_value != debit_value:
    #         # for supplier returns of product in average costing method, in anglo saxon mode
    #         diff_amount = debit_value - credit_value
    #         price_diff_account = self.product_id.property_account_creditor_price_difference

    #         if not price_diff_account:
    #             price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
    #         if not price_diff_account:
    #             raise UserError(
    #                 _('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))

    #         rslt['price_diff_line_vals'] = {
    #             'name': self.name,
    #             'product_id': self.product_id.id,
    #             'quantity': qty,
    #             'product_uom_id': self.product_id.uom_id.id,
    #             'ref': ref,
    #             'partner_id': partner_id,
    #             'credit': diff_amount > 0 and diff_amount or 0,
    #             'debit': diff_amount < 0 and -diff_amount or 0,
    #             'account_id': price_diff_account.id,
    #         }
    #     return rslt


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
