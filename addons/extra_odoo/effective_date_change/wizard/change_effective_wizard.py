from odoo import api, models, fields
from .query import QueryList
from .function import *
from datetime import datetime
from odoo.exceptions import UserError


class ChangeEffectiveWizard(models.TransientModel):
    _name = "change.effective.wizard"

    # Definisikan field wizard
    effective_date = fields.Datetime(string="Fecha Efectiva", help="Date at which the transfer is processed")
    rewrite_related_picking = fields.Boolean(string="Cambiar a Todos los Pickings (Misma Order)", default=False, help="Also Apply to Other Stock Picking Which Has the Same Source Document Name")

    # Onchange sebagai reminder ketika memilih tanggal masa depan untuk memilih tanggal di masa lalu saja
    @api.onchange('effective_date')
    def effective_future(self):
        selected = self.env['stock.picking'].browse(self._context.get('active_ids', []))
        current_date = datetime.now()

        # Bandingkan tanggal hari ini dengan tanggal yang terpilih
        # Jika tanggal tidak sesuai (lebih ke masa depan) maka tidak bisa proses
        if self.effective_date and self.effective_date > current_date:
            raise UserError('The date selected is still in the future. Make sure to only do a backdate!')

    # Simpan record
    def update_effective_date(self):
        query = QueryList()  # instantiation query

        # Memanggil record active_id ke dalam transient model
        for picking in self.env['stock.picking'].browse(self._context.get('active_ids', [])):

            # Mendefinisikan field yang ada di wizard (model.Transient)
            picking_name = picking.name
            wildcard_picking_name = concat(picking_name)
            picking_source_document = picking.origin
            selected_effective_date = self.effective_date

            # Melakukan pengecekan internal atau eksternal transfer
            # Jika picking_source_document ada, maka itu adalah eksternal transfer
            if picking_source_document:
                # Jika rewrite_related_picking tidak dicentang, maka update satu picking terpilih saja
                if self.rewrite_related_picking == False:
                    # Update picking
                    do_update(query.update_stock_picking_by_name, self.effective_date, picking_name)

                    # Update Sale Order
                    do_update(query.update_sale_order, self.effective_date, picking_source_document)

                    # Update Purchase Order
                    do_update(query.update_purchase_order, self.effective_date, picking_source_document)

                    # Update account_move date
                    do_update(query.update_journal_entry, self.effective_date, wildcard_picking_name)

                    # Update account_move (journal entry)
                    stj_account_move_find_sequence = account_move_concat(str(selected_effective_date.year), str(selected_effective_date.month))
                    stj_account_move_sequences = [stj_account_move for stj_account_move in self.env['account.move'].search([('name', 'ilike', stj_account_move_find_sequence)]).mapped('name')]
                    if stj_account_move_sequences == []:
                        ids = self.env['account.move'].search([('ref', 'ilike', wildcard_picking_name), ('company_id', '=', self.company_id.id)]).mapped('id')
                        number = 1
                        while number <= len(ids):
                            for id in ids:
                                stj_account_move_new_name = account_move_new_name(str(selected_effective_date.year), str(selected_effective_date.month), str(number))
                                self.env.cr.execute("UPDATE account_move SET name = (%s) WHERE id = (%s)", [stj_account_move_new_name, id])
                                number += 1
                    else:
                        stj_sequences_max = str(max(stj_account_move_sequences))
                        stj_sequences_trim = int(stj_sequences_max.replace(stj_account_move_find_sequence, ''))
                        stj_sequences_addition = stj_sequences_trim + 1

                        ids = self.env['account.move'].search([('ref', 'ilike', wildcard_picking_name), ('company_id', '=', self.company_id.id)]).mapped('id')
                        starter = stj_sequences_addition
                        number = 1
                        while number <= len(ids):
                            for id in ids:
                                stj_account_move_new_name = account_move_new_name(str(selected_effective_date.year), str(selected_effective_date.month), str(starter))
                                self.env.cr.execute("UPDATE account_move SET name = (%s) WHERE id = %s", [stj_account_move_new_name, id])
                                starter += 1
                                number += 1

                    # Update account_move_line
                    do_update(query.update_journal_entry_line, self.effective_date, wildcard_picking_name)

                    # Update stock_move
                    do_update(query.update_stock_move, self.effective_date, picking_name)

                    # Update stock_move_line
                    do_update(query.update_stock_move_line, self.effective_date, picking_name)

                    # Update stock valuation
                    for stock_move_id in self.env['stock.move'].search([('reference','=', picking_name), ('company_id', '=', self.company_id.id)]):
                        do_update(query.update_inventory_valuation_date, self.effective_date, int(stock_move_id))

                    # Account Move Update if foreign currency
                    # Ambil dulu system currency (dari company) dan foreign country (dari PO atau SO)
                    company_id = self.env['stock.picking'].search([]).company_id.id
                    system_currency = self.env['res.company'].search([('id', '=', company_id)]).currency_id.id
                    po_currency = self.env['purchase.order'].search([('name', '=', picking_source_document), ('company_id', '=', self.company_id.id)]).currency_id
                    so_currency = self.env['sale.order'].search([('name', '=', picking_source_document), ('company_id', '=', self.company_id.id)]).currency_id

                    foreign_currency = po_currency.id if po_currency.id != False else None or so_currency.id if so_currency.id != False else None

                    if system_currency != foreign_currency:
                        # Ambil currency rate berdasarkan tanggal yang dipilih & tentukan ratenya
                        currency_rate = self.env['res.currency.rate'].search([('currency_id', '=', foreign_currency), ('name', '=', selected_effective_date.strftime('%Y-%m-%d'))]).rate
                        try:
                            currency_value = 1 / float(currency_rate)
                        except:
                            raise UserError('You have selected the currency rate of '+ str(po_currency.name or so_currency.name) +' which is currently not available based on your selected date. Make sure to fill it under Accounting > Settings > Currencies > ' + str(po_currency.name or so_currency.name) +'!')

                        purchase_orders_id = self.env['purchase.order'].search([('name', '=', picking_source_document), ('company_id', '=', self.company_id.id)]).id  # Cari ID PO
                        sales_orders_id = self.env['sale.order'].search([('name', '=', picking_source_document)]).id  # Cari ID SO
                        orders_id = purchase_orders_id if purchase_orders_id != False else None or sales_orders_id if sales_orders_id != False else None

                        for stock_move_id_two in self.env['stock.move'].search([('reference', '=', picking_name), ('company_id', '=', self.company_id.id)]):  # Cari stock_move ID pakai picking_name
                            for stock_valuation in self.env['stock.valuation.layer'].search([('stock_move_id', '=', stock_move_id_two.id)]):  # Cari stock valuation
                                po_price_unit = self.env['purchase.order.line'].search([('order_id', '=', orders_id), ('product_id', '=', stock_valuation.product_id.id)])
                                so_price_unit = self.env['sale.order.line'].search([('order_id', '=', orders_id),('product_id', '=', stock_valuation.product_id.id)])
                                orders_price_unit = po_price_unit if po_price_unit != False else None or so_price_unit if so_price_unit != False else None
                                unit_value = float(currency_value) * float(orders_price_unit.price_unit)
                                stock_valuation.unit_cost = unit_value
                                stock_valuation.value = stock_valuation.quantity * unit_value
                                stock_valuation.remaining_value = unit_value * stock_valuation.remaining_qty

                        # Ubah account_move_line debit credit
                        acc_move_line = self.env['account.move.line'].search([('ref', 'like', picking_name), ('company_id', '=', self.company_id.id)])
                        for id in acc_move_line:
                            po_price_unit = self.env['purchase.order.line'].search([('order_id', '=', orders_id), ('product_id', '=', id.product_id.id)])
                            so_price_unit = self.env['sale.order.line'].search([('order_id', '=', orders_id), ('product_id', '=', id.product_id.id)])
                            orders_price_unit = po_price_unit if po_price_unit != False else None or so_price_unit if so_price_unit != False else None

                            if id.credit != 0:
                                aydi_credit = float(currency_value) * float(id.quantity) * float(orders_price_unit.price_unit)
                                id.with_context(check_move_validity=False).write({'credit': abs(aydi_credit)})

                            if id.debit != 0:
                                aydi_debit = float(currency_value) * float(id.quantity) * float(orders_price_unit.price_unit)
                                id.with_context(check_move_validity=False).write({'debit': abs(aydi_debit)})

                else:
                    do_query(query.find_name_from_stock_picking, picking_source_document)
                    stock_picking = [pulled_stock_picking_as_row[0] for pulled_stock_picking_as_row in self.env.cr.fetchall()]
                    percentage_stock_picking = [pickings_found + "%" for pickings_found in stock_picking]

                    pulled_stock_picking_tuples = tuple(stock_picking)
                    if pulled_stock_picking_tuples == ():
                        # Not changing anything because origin is not set
                        pass
                    else:
                        # Update stock_picking
                        do_update(query.update_stock_picking_by_origin, self.effective_date, picking_source_document)

                        # Update sale_order
                        do_update(query.update_sale_order, self.effective_date, picking_source_document)

                        # Update purchase_order
                        do_update(query.update_purchase_order, self.effective_date, picking_source_document)

                        # Update account_move date
                        do_update(query.update_journal_entry_by_ref_tuple, self.effective_date, percentage_stock_picking)

                        # Update account_move name
                        stj_account_move_find_sequence = account_move_concat(str(selected_effective_date.year), str(selected_effective_date.month))
                        stj_account_move_sequences = [stj_account_move for stj_account_move in self.env['account.move'].search( [('name', 'ilike', stj_account_move_find_sequence)]).mapped('name')]

                        if stj_account_move_sequences == []:
                            print("Generate dari awal")
                            ids = self.env['account.move'].search([('ref', 'ilike', wildcard_picking_name), ('company_id', '=', self.company_id.id)]).mapped('id')
                            number = 1
                            while number <= len(ids):
                                for id in ids:
                                    stj_account_move_new_name = account_move_new_name(str(selected_effective_date.year), str(selected_effective_date.month), str(number))
                                    self.env.cr.execute("UPDATE account_move SET name = (%s) WHERE id = (%s)", [stj_account_move_new_name, id])
                                    number += 1
                        else:
                            print("Lanjutkan nomor sebelumnya")
                            stj_sequences_max = str(max(stj_account_move_sequences))
                            stj_sequences_trim = int(stj_sequences_max.replace(stj_account_move_find_sequence, ''))
                            stj_sequences_addition = stj_sequences_trim + 1

                            ids = self.env['account.move'].search([('ref', 'ilike', wildcard_picking_name), ('company_id', '=', self.company_id.id)]).mapped('id')
                            starter = stj_sequences_addition
                            number = 1
                            while number <= len(ids):
                                for id in ids:
                                    stj_account_move_new_name = account_move_new_name(str(selected_effective_date.year), str(selected_effective_date.month), str(starter))
                                    self.env.cr.execute("UPDATE account_move SET name = (%s) WHERE id = %s", [stj_account_move_new_name, id])
                                    starter += 1
                                    number += 1

                        # Update account_move_line
                        do_update(query.update_journal_entry_line_by_ref_tuple, self.effective_date, percentage_stock_picking)

                        # Update Stock Move
                        do_update(query.update_stock_move_by_ref_tuple, self.effective_date, pulled_stock_picking_tuples)

                        # Update stock move line
                        do_update(query.update_stock_move_line_by_ref_tuple, self.effective_date, pulled_stock_picking_tuples)

                        # Update stock valuation
                        for pickings in stock_picking:
                            for stock_move_id in self.env['stock.move'].search([('reference', '=', pickings), ('company_id', '=', self.company_id.id)]):
                                do_update(query.update_inventory_valuation_date, self.effective_date, int(stock_move_id))
                                print(f"stock picking dengan nomor {pickings} dan stock move id {stock_move_id} telah berhasil diganti")

                        # Account Move Update if foreign currency
                        # Ambil dulu system currency (dari company) dan foreign country (dari PO)
                        company_id = self.env['stock.picking'].search([]).company_id.id
                        system_currency = self.env['res.company'].search([('id', '=', company_id)]).currency_id.id
                        po_currency = self.env['purchase.order'].search([('name', '=', picking_source_document), ('company_id', '=', self.company_id.id)]).currency_id
                        so_currency = self.env['sale.order'].search([('name', '=', picking_source_document), ('company_id', '=', self.company_id.id)]).currency_id

                        foreign_currency = po_currency.id if po_currency.id != False else None or so_currency.id if so_currency.id != False else None

                        if system_currency != foreign_currency:
                            # Ambil currency rate berdasarkan tanggal yang dipilih & tentukan ratenya
                            currency_rate = self.env['res.currency.rate'].search(
                                [('currency_id', '=', foreign_currency), ('name', '=', selected_effective_date.strftime('%Y-%m-%d'))]).rate
                            try:
                                currency_value = 1 / float(currency_rate)
                            except:
                                raise UserError('You have selected the currency rate of ' + str(po_currency.name or so_currency.name) + ' which is currently not available based on your selected date. Make sure to fill it under Accounting > Settings > Currencies > ' + str(
                                    po_currency.name or so_currency.name) + '!')

                            purchase_orders_id = self.env['purchase.order'].search([('name', '=', picking_source_document), ('company_id', '=', self.company_id.id)]).id  # Cari ID PO
                            sales_orders_id = self.env['sale.order'].search([('name', '=', picking_source_document)]).id  # Cari ID SO
                            orders_id = purchase_orders_id if purchase_orders_id != False else None or sales_orders_id if sales_orders_id != False else None

                            # Ubah valuasi di stock valuation produk
                            # for orders_price_unit in self.env['purchase.order.line'].search([('order_id', '=', orders_id)]):
                            for stock_move_id_two in self.env['stock.move'].search([('origin', '=', picking_source_document), ('company_id', '=', self.company_id.id)]):  # Cari stock_move ID pakai nama PO
                                for stock_valuation in self.env['stock.valuation.layer'].search([('stock_move_id', '=', stock_move_id_two.id)]):  # Cari stock valuation
                                    po_price_unit = self.env['purchase.order.line'].search([('order_id', '=', orders_id),('product_id', '=', stock_valuation.product_id.id)])
                                    so_price_unit = self.env['sale.order.line'].search([('order_id', '=', orders_id), ('product_id', '=', stock_valuation.product_id.id)])
                                    orders_price_unit = po_price_unit if po_price_unit != False else None or so_price_unit if so_price_unit != False else None

                                    unit_value = float(currency_value) * float(orders_price_unit.price_unit)
                                    stock_valuation.unit_cost = unit_value
                                    stock_valuation.value = stock_valuation.quantity * unit_value
                                    stock_valuation.remaining_value = unit_value * stock_valuation.remaining_qty

                            # Ubah account_move_line debit credit
                            for picking_list in self.env['stock.picking'].search([('origin', '=', picking_source_document), ('company_id', '=', self.company_id.id)]):
                                for acc_move_line in self.env['account.move.line'].search([('ref', 'like', str(picking_list.name), ('company_id', '=', self.company_id.id))]):
                                    for id in acc_move_line:
                                        po_price_unit = self.env['purchase.order.line'].search([('order_id', '=', orders_id), ('product_id', '=', id.product_id.id)])
                                        so_price_unit = self.env['sale.order.line'].search([('order_id', '=', orders_id), ('product_id', '=', id.product_id.id)])
                                        orders_price_unit = po_price_unit if po_price_unit != False else None or so_price_unit if so_price_unit != False else None

                                        if id.credit != 0:
                                            aydi_credit = float(currency_value) * float(id.quantity) * float(orders_price_unit.price_unit)
                                            id.with_context(check_move_validity=False).write({'credit': abs(aydi_credit)})

                                        if id.debit != 0:
                                            aydi_debit = float(currency_value) * float(id.quantity) * float(orders_price_unit.price_unit)
                                            id.with_context(check_move_validity=False).write({'debit': abs(aydi_debit)})

            else:
                # Update internal transfer
                do_update(query.update_stock_picking_by_name, self.effective_date, picking_source_document)

                # Update stock move
                do_update(query.update_stock_move, self.effective_date, picking_source_document)

                # Update stock_move_line
                do_update(query.update_stock_move_line, self.effective_date, picking_source_document)

