from dateutil.parser import *
from odoo import api, fields, models, _
import requests
import ast
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import datetime, timedelta
import logging
import re
import json
import pandas as pd

import base64
import os

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.model
    def create(self, vals):
        if vals['type'] == 'sale':
            sequence_id = self.env['ir.sequence'].search(
                [('code', '=', 'invoice_sequencing')])
            # print (" ----------------------------------------- ", sequence_id)
            vals['sequence'] = sequence_id.id
        res = super(AccountJournal, self).create(vals)
        return res

    # @api.multi
    def write(self, vals):
        # print ("Self ---------------------------------------------", self)
        if 'type' in vals:
            if vals['type'] == 'sale':
                sequence_id = self.env['ir.sequence'].search(
                    [('code', '=', 'invoice_sequencing')])
                # print (" ----------------------------------------- ", sequence_id)
                vals['sequence'] = sequence_id.id
        elif self.type == 'sale':
            sequence_id = self.env['ir.sequence'].search(
                [('code', '=', 'invoice_sequencing')])
            # print (" ----------------------------------------- ", sequence_id)
            vals['sequence'] = sequence_id.id
        res = super(AccountJournal, self).write(vals)
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    qbd_tax_code = fields.Many2one('qbd.tax.code')

    @api.depends('product_id')
    def _compute_product_uom_id(self):
        super(AccountInvoiceLine, self)._compute_product_uom_id()
        vals = {}
        if self.tax_ids:
            vals['qbd_tax_code'] = self.tax_ids[0].qbd_tax_code.id
        self.update(vals)

    @api.onchange('tax_ids')
    def _onchange_tax_id(self):
        vals = {}
        if self.tax_ids:
            vals['qbd_tax_code'] = self.tax_ids[0].qbd_tax_code.id
            self.update(vals)

    # @api.model
    # def write(self, vals):
    #     _logger.info("VALS===>>>>>>>>>>>>>>>>>>>>>>>{}".format(vals))
    #     return super(AccountInvoiceLine, self).write(vals)


class AccountInvoice(models.Model):
    _inherit = "account.move"

    quickbooks_id = fields.Char("Quickbook id ", copy=False)
    qbd_number = fields.Char("QBD INV No.", copy=False)
    is_updated = fields.Boolean('Is Updated')
    lpo_no = fields.Char('LPO #', copy=False)
    veh_or_w_bill = fields.Char('VEH/W.BILL#', copy=False)
    etr_no = fields.Char('ETR #', copy=False)
    qbd_tax = fields.Many2one('account.tax', string="QBD Tax", copy=False)

    # def _check_balanced(self):
    #     ''' Assert the move is fully balanced debit = credit.
    #     An error is raised if it's not the case.
    #     '''
    #     moves = self.filtered(lambda move: move.line_ids)
    #     if not moves:
    #         return

    #     # /!\ As this method is called in create / write, we can't make the assumption the computed stored fields
    #     # are already done. Then, this query MUST NOT depend of computed stored fields (e.g. balance).
    #     # It happens as the ORM makes the create with the 'no_recompute' statement.
    #     self.env['account.move.line'].flush(
    #         self.env['account.move.line']._fields)
    #     self.env['account.move'].flush(['journal_id'])
    #     self._cr.execute('''
    #         SELECT line.move_id, ROUND(SUM(line.debit - line.credit), currency.decimal_places)
    #         FROM account_move_line line
    #         JOIN account_move move ON move.id = line.move_id
    #         JOIN account_journal journal ON journal.id = move.journal_id
    #         JOIN res_company company ON company.id = journal.company_id
    #         JOIN res_currency currency ON currency.id = company.currency_id
    #         WHERE line.move_id IN %s
    #         GROUP BY line.move_id, currency.decimal_places
    #         HAVING ROUND(SUM(line.debit - line.credit), currency.decimal_places) >= 0.5;
    #     ''', [tuple(self.ids)])

    #     query_res = self._cr.fetchall()
    #     # print('query_res : ', query_res)
    #     if query_res:
    #         ids = [res[0] for res in query_res]
    #         sums = [res[1] for res in query_res]
    #         raise UserError(
    #             _("Cannot create unbalanced journal entry. Ids: %s\nDifferences debit - credit: %s") % (ids, sums))

    def write_taxcode(self, res):
        for rec in res.invoice_line_ids:
            move_line_obj = self.env['account.move.line'].search([('id', '=', rec.id)])
            print("Lineeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", rec)
            if rec.tax_ids:
                _logger.info("TAX IDS===>>>>>>>>>>{}".format(rec.tax_ids))
                move_line_obj.qbd_tax_code = rec.tax_ids[0].qbd_tax_code.id
                _logger.info("ACCOUNT LINE ===>>>>>>>>>>>>>>>>>>>>{}".format(
                    move_line_obj.qbd_tax_code))

    @api.model
    def create(self, vals):
        # print("\n\n in createeeeeeeeeeeeeeeeeeeeeee of invoice",vals)
        res = super(AccountInvoice, self).create(vals)
        self.write_taxcode(res)
        _logger.info("RES===>>>>>>>>>>>>>>>>>>>>{}".format(res))
        return res

    def write(self, vals):
        # print("\n\n in create of invoice",self, vals)
        if 'is_updated' not in vals and 'quickbooks_id' not in vals and 'state' not in vals and 'invoice_date' not in vals and 'invoice_date_due' not in vals and 'move_id' not in vals and 'move_name' not in vals and 'ref' not in vals:  # and 'date' not in vals
            vals['is_updated'] = True
        self.write_taxcode(self)
        return super(AccountInvoice, self).write(vals)

    def combine_invoices_and_lines(self, invoice_file, line_file):
        # Leemos los archivos CSV usando Pandas
        df_invoices = pd.read_csv("/tmp/"+ invoice_file)
        df_lines = pd.read_csv("/tmp/"+ line_file)
        
        combined_data = []

        # Iteramos sobre cada factura
        for _, invoice_row in df_invoices.iterrows():
            invoice_dict = invoice_row.to_dict()
            # Filtramos las líneas de factura que corresponden a esta factura
            matching_lines = df_lines[df_lines['TxnID'] == invoice_dict['quickbooks_id']]
            # Convertimos el DataFrame filtrado a una lista de diccionarios
            invoice_lines_list = matching_lines.drop(columns=['TxnID']).to_dict(orient='records')
            # Agregamos esta lista de líneas de factura al diccionario de la factura
            invoice_dict['invoice_lines'] = invoice_lines_list
            combined_data.append(invoice_dict)

        return combined_data

    def save_csv(self, data):
        
        base64_csv1 = data['invoice_file']
        base64_csv2 = data['line_file']
        
        csv1_bytes = base64.b64decode(base64_csv1)
        csv2_bytes = base64.b64decode(base64_csv2)
        path_to_tmp = '/tmp'  # Puedes cambiar esto por cualquier ruta donde tengas permisos de escritura
        csv1_name = 'invoice_file.csv'
        csv2_name = 'line_file.csv'
        csv1_path = os.path.join(path_to_tmp, csv1_name)
        csv2_path = os.path.join(path_to_tmp, csv2_name)
                
        with open(csv1_path, 'wb') as file:
            file.write(csv1_bytes)

        with open(csv2_path, 'wb') as file:
            file.write(csv2_bytes)
            
        data = self.combine_invoices_and_lines(csv1_name, csv2_name)
        
        return data
        
        
    def create_invoice(self, data):
        company = self.env['res.users'].search([('id', '=', 2)]).company_id
        journal_id = self.env['account.journal'].search(
            [('type', '=', 'sale')])
        if not journal_id:
            raise ValidationError('Please create journal of type sale ..')
        
        if data:
            invoices = self.save_csv(data)
            if isinstance(invoices, list) and len(invoices) >= 1:
                last_record_inv = invoices[-1]

                for invoice in invoices:
                    # print(invoice)
                    vals = {}
                    # print('\ninvoice data : \n\n', invoice)
                    if 'quickbooks_id' in invoice and invoice.get('quickbooks_id'):
                        invoice_id = self.search(
                            [('quickbooks_id', '=', invoice.get('quickbooks_id'))], limit=1)

                        if not invoice_id:
                            # create new SO
                            vals = self._prepare_invoice_dict(invoice)

                            if vals:
                                new_invoice_id = self.create(vals)

                                if 'invoice_lines' in invoice and invoice.get('invoice_lines'):
                                    invoice_lines = invoice.get('invoice_lines')
                                    invoice_line_id = self.create_invoice_lines(
                                        invoice_lines, new_invoice_id)

                                if new_invoice_id:
                                    new_invoice_id.write({'state': 'draft'})
                                # if new_invoice_id.invoice_line_ids:
                                #     new_invoice_id.action_invoice_open()
                                #     new_invoice_id._onchange_invoice_line_ids()

                                if new_invoice_id:
                                    self.env.cr.commit()
                                    # print('New Invoice Commited :: ', new_invoice_id.name)
                                    date_parsed = parse(
                                        invoice.get("last_time_modified"))
                                    company.write({
                                        'last_imported_qbd_id_for_invoice': date_parsed
                                    })

                                    # if invoice.get('state') == 'paid':
                                    #     if 'confirmation_date' in order and order.get('confirmation_date'):
                                    #         new_sale_order_id.write({'confirmation_date': order.get('confirmation_date')})

                        if invoice_id:
                            #     # update existing SO
                            #     # print('\nUpdate existing  invoice')
                            vals = self._prepare_invoice_dict(invoice)
                            invoice_id.write(vals)
                            if 'invoice_lines' in invoice and invoice.get('invoice_lines'):
                                invoice_lines = invoice.get('invoice_lines')
                                invoice_line_id = self.update_invoice_lines(
                                    invoice_lines, invoice_id)
                            #         invoice_id._onchange_invoice_line_ids()
                            company.write({
                                'last_imported_qbd_id_for_invoice': invoice.get("last_time_modified")
                            })
                            # If the records is getting repeated this will inc the limit and try to fetch the new records
                            #    which will have other modified date to resolve the conflict of importing same data ####
                            if invoice_id.quickbooks_id == last_record_inv.get('quickbooks_id'):
                                if last_record_inv.get('last_time_modified') == company.last_imported_qbd_id_for_invoice:
                                    _logger.info("AGAIN GONE FOR REQUEST INVOICE")

                                    limit_rec_import = int(
                                        company.import_inv_limit) + int(company.import_inv_limit)

                                    _logger.info(
                                        "Limit REC IMPORT====>>>>>>>>>>>>>>>>{}".format(limit_rec_import))
                                    if limit_rec_import >= 50:
                                        company.write({'import_inv_limit': 10})
                                        return True
                                    else:
                                        company.write(
                                            {'import_inv_limit': limit_rec_import})
                                        company.import_invoice(limit_rec_import)
            return True

    def create_vendor_bill(self, vendor_bill):
        company = self.env['res.users'].search([('id', '=', 2)]).company_id
        journal_id = self.env['account.journal'].search([('type', '=', 'purchase')])
        is_vendor_bill = True
        if not journal_id:
            raise UserError('Please create journal of type Purchase ..')
        for bill in vendor_bill:
            vals = {}
            if 'quickbooks_id' in bill and bill.get('quickbooks_id'):
                vendor_bill_id = self.search(
                    [('quickbooks_id', '=', bill.get('quickbooks_id'))], limit=1)

                if not vendor_bill_id:
                    # create new SO
                    # print('\nCreate New Sale invoice')
                    # print('invoice dict : ', invoice, '\n')
                    vals = self._prepare_invoice_dict(bill, is_vendor_bill)

                    if vals:
                        new_invoice_id = self.create(vals)

                        if 'invoice_lines' in bill and bill.get('invoice_lines'):
                            invoice_lines = bill.get('invoice_lines')
                            invoice_line_id = self.create_invoice_lines(
                                invoice_lines, new_invoice_id)

                        if new_invoice_id:
                            new_invoice_id.write({'state': 'draft'})

                        if new_invoice_id:
                            self.env.cr.commit()
                            # print('New Invoice Commited :: ', new_invoice_id.name)
                            company.write({
                                'last_imported_qbd_id_for_vendor_bill': bill.get("last_time_modified")
                            })


    
    
    def _prepare_invoice_dict(self, invoice, is_vendor_bill=None):
        vals = {}
        _logger.info("\n\n\n\n\n\n\nINVOICE===>>>>>>>>>>>>>>>>>>{}".format(invoice))
        if invoice.get('qbd_tax'):
            tax_id = self.env['account.tax'].search(
                [('quickbooks_id', '=', invoice.get('qbd_tax'))])
            _logger.info("TAX ===>>>>>>>>>>>>{}".format(tax_id))
        if invoice:
            vals.update({
                'quickbooks_id': invoice.get('quickbooks_id') if invoice.get('quickbooks_id') else '',
                'invoice_date_due': invoice.get('date_due') if invoice.get('date_due') else '',
                'qbd_number': invoice.get('number') if invoice.get('number') else '',
                'lpo_no': invoice.get('po_number') if invoice.get('po_number') else '',
                'etr_no': invoice.get('etr_number') if invoice.get('etr_number') else '',
                'veh_or_w_bill': invoice.get('veh_bill') if invoice.get('veh_bill') else '',
                'ref' : invoice.get('ref') if invoice.get('ref') else ''
            })
            if invoice.get('qbd_tax'):
                vals.update({'qbd_tax': tax_id.id})
            if is_vendor_bill:
                vals.update({'move_type': 'in_invoice'})
            else:
                vals.update({'move_type': 'out_invoice'})

            # print("Invoice Vals==>>>", vals)
            if 'partner_name' in invoice and invoice.get('partner_name'):
                partner_id = self.env['res.partner'].search([('quickbooks_id', '=', invoice.get('partner_name')), ('active', 'in', [True, False])],
                                                            limit=1)

                if partner_id:
                    vals.update({'partner_id': partner_id.id})
                else:
                    company_id = self.env.user.company_id
                    partner_id = company_id.import_partner(
                        invoice.get('partner_name'))
                    if partner_id:
                        vals.update({'partner_id': partner_id.id})
            if 'term_name' in invoice and invoice.get('term_name'):
                term_id = self.env['account.payment.term'].search(
                    [('name', '=', invoice.get('term_name'))])

                if term_id:
                    vals.update(({'invoice_payment_term_id': term_id.id}))

            if 'currency' in invoice and invoice.get('currency'):
                currency_id = self.env.ref('base.' + invoice.get('currency'))
                company_currency = self.env.user.company_id.currency_id
                if currency_id != company_currency:
                    vals.update({
                        'currency_id': currency_id.id,
                        'apply_manual_currency_exchange': True,
                        'active_manual_currency_rate': True,
                        'manual_currency_exchange_rate': float(invoice.get('rate'))
                    })

            if 'invoice_date' in invoice and invoice.get('invoice_date'):
                vals.update({'invoice_date': invoice.get('invoice_date')})

        if vals:
            return vals

    def create_invoice_lines(self, invoice_lines, invoice_id):
        invoice_line_id_list = []
        company = self.env['res.users'].search([('id', '=', 2)]).company_id

        if invoice_lines:
            for line in invoice_lines:
                _logger.info(_('\n\nline IDs : %s' % line))
                vals_ol = {}
                vals_col = {}
                vals_tol = {}

                if invoice_id:
                    vals_ol.update({'move_id': invoice_id.id})
                    vals_col.update({'move_id': invoice_id.id})
                    vals_tol.update({'move_id': invoice_id.id})

                if 'product_name' in line and line.get('product_name'):
                    product_id = self.env['product.product'].search(
                        [('quickbooks_id', '=', line.get('product_name'))])

                    if product_id:
                        vals_ol.update({'product_id': product_id.id})
                        vals_col.update({'product_id': False})
                        vals_tol.update({'product_id': False})
                    if 'tax_code' in line and line.get('tax_code'):
                        print("TAX CODE", line.get('tax_code'))
                        tax_code = self.env['qbd.tax.code'].search(
                            [('name', '=', line.get('tax_code'))])
                        if tax_code:
                            vals_ol.update({'qbd_tax_code': tax_code.id})
                        _logger.info(_("\n\n tax_code : %s" % tax_code))

                        if tax_code.is_taxable and tax_code.quickbooks_id:
                            tax_id = self.env['account.tax'].search(
                                [('quickbooks_id', '=', tax_code.quickbooks_id)], limit=1)
                            if tax_id:
                                _logger.info(_('Got Tax : %s' % tax_id))
                                vals_ol.update(
                                    {'tax_ids': [(6, 0, [tax_id.id])]})
                                vals_col.update({'tax_ids': False})
                                vals_tol.update({'tax_ids': False})
                            else:
                                _logger.warning('Tax Error')
                    else:
                        vals_ol.update({'tax_ids': False})
                        vals_col.update({'tax_ids': False})
                        vals_tol.update({'tax_ids': False})

                    if product_id.property_account_income_id:
                        vals_ol.update(
                            {'account_id': product_id.property_account_income_id.id})
                    elif product_id.categ_id.property_account_income_categ_id:
                        vals_ol.update(
                            {'account_id': product_id.categ_id.property_account_income_categ_id.id})
                    else:
                        vals_ol.update(
                            {'account_id': company.qb_income_account.id})

                    if invoice_id.partner_id.property_account_receivable_id:
                        vals_col.update(
                            {'account_id': invoice_id.partner_id.property_account_receivable_id.id})
                        vals_tol.update(
                            {'account_id': invoice_id.partner_id.property_account_receivable_id.id})
                else:
                    continue

                vals_ol.update({
                    'quantity': float(line.get('quantity')) if line.get('quantity') else 0.00,
                    # 'exclude_from_invoice_tab': False,
                })

                if line.get('name'):
                    string = line.get('name')
                    _logger.info("LINE DESC===>>>>>>>>>>>{}".format(string))
                    text = self.cleanup_productdesc(string)
                    # _logger.info("TEXT===>>>>>>>>>>>>{}".format(text))
                    vals_ol.update({
                        'name': text if text else '',
                    })
                vals_col.update({
                    'quantity': float(line.get('quantity')) if line.get('quantity') else 0.00,
                    'name': False,
                    # 'exclude_from_invoice_tab': True,
                })

                vals_tol.update({
                    'quantity': float(line.get('quantity')) if line.get('quantity') else 0.00,
                    'name': False,
                    # 'exclude_from_invoice_tab': True,
                })

                if 'price_unit' in line and line.get('price_unit') != 'None':
                    price_unit = float(line.get('price_unit'))
                    # if company.currency_id != invoice_id.currency_id:
                    #     price_unit = price_unit * invoice_id.manual_currency_exchange_rate
                            
                    vals_ol.update(
                        {'price_unit': price_unit})
                    vals_col.update(
                        {'price_unit': -(price_unit)})

                    # vals_ol.update(
                    #     {'credit': abs(vals_ol['quantity']) * abs(price_unit)})
                    # vals_ol.update({'debit': 0})

                    # vals_col.update({'credit': 0})
                    # vals_col.update(
                    #     {'debit': abs(vals_col['quantity']) * abs(price_unit)})
                else:
                    vals_ol.update({'price_unit': 0})
                    vals_col.update({'price_unit': 0})

                    # vals_ol.update({'credit': 0})
                    # vals_ol.update({'debit': 0})

                    # vals_col.update({'credit': 0})
                    # vals_col.update({'debit': 0})

                if vals_ol.get('tax_ids'):
                    tax_amount = tax_id.amount
                    vals_tol['price_unit'] = abs(
                        float(vals_ol['quantity']) * vals_ol['price_unit'] * float(tax_amount / 100))
                    vals_tol['credit'] = vals_tol['price_unit']
                    vals_tol['debit'] = 0

                    vals_col['debit'] += vals_tol['credit']

                    vals_ol['tax_repartition_line_id'] = False
                    vals_col['tax_repartition_line_id'] = False
                    tax_repartition_line_id = self.env['account.tax.repartition.line'].search(
                        [('repartition_type', '=', 'tax')], limit=1)
                    vals_tol['tax_repartition_line_id'] = tax_repartition_line_id.id

                    vals_ol['tax_base_amount'] = 0
                    vals_col['tax_base_amount'] = 0
                    vals_tol['tax_base_amount'] = vals_ol['quantity'] * \
                        vals_ol['price_unit']
                else:
                    vals_tol.update({'price_unit': 0})
                    vals_tol.update({'credit': 0})
                    vals_tol.update({'debit': 0})

                if vals_ol and vals_col:
                    data = []
                    print("VALS OL===>>>", vals_ol)
                    data.append(vals_ol)
                    print("VALS COL===>>>", vals_col)
                    data.append(vals_col)
                    if vals_ol.get('tax_ids'):
                        data.append(vals_tol)
                    _logger.info(_('\n\n data : %s ' % data))
                    invoice_line_id = self.env['account.move.line'].create(
                        data)

                    _logger.info(
                        _("5----------------------------------------------------------\n\n%s\n" % invoice_line_id))
                    # invoice_line_id._compute_price()
                    if invoice_line_id:
                        invoice_line_id_list.append(invoice_line_id)
        if invoice_line_id_list:
            return invoice_line_id_list

    def cleanup_productdesc(self, string):
        """
            This Method will cleanup the Byte character from the Order line Description field
        """
        try:
            text = re.sub("[^\x20-\x7E]", "", string)
            text.strip()
        except Exception as e:
            raise UserError(e)
        return text

    def update_invoice_lines(self, invoice_lines, invoice_id):
        # print('In update invoice method: ',invoice_id)
        invoice_line_id = None
        company = self.env['res.users'].search([('id', '=', 2)]).company_id

        product_qbd_id_list = []
        if invoice_id:
            for invoice_line in invoice_id.invoice_line_ids:
                product_qbd_id_list.append(invoice_line.product_id.quickbooks_id)

            for line in invoice_lines:
                if line.get('product_name') not in product_qbd_id_list:
                    # print('If product not found in line so create new product')
                    vals = {}

                    vals.update({'invoice_id': invoice_id.id})

                    if 'product_name' in line and line.get('product_name'):
                        product_id = self.env['product.product'].search(
                            [('quickbooks_id', '=', line.get('product_name'))])

                        if product_id:
                            vals.update({
                                'product_id': product_id.id
                            })

                        else:
                            continue

                        if product_id.property_account_income_id:
                            vals.update(
                                {'account_id': product_id.property_account_income_id.id})
                        elif product_id.categ_id.property_account_income_categ_id:

                            vals.update(
                                {'account_id': product_id.categ_id.property_account_income_categ_id.id})
                        else:
                            vals.update({'account_id': company.qb_income_account.id})
                    else:
                        continue
                    
                  
                    vals.update({
                        'price_unit': float(line.get('price_unit')) if line.get('price_unit') else 0.00,
                        'quantity': float(line.get('quantity')) if line.get('quantity') else 0.00,
                        'name': line.get('name') if line.get('name') else '',
                    })

                    if vals:
                        invoice_line_id = self.env['account.move.line'].create(vals)

        if invoice_line_id:
            return True

    # @api.multi

    def export_invoices(self, invoice_lst=False, is_vendor_bill=False):
        # print('Export Invoices !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        loger_dict = {}
        company = self.env['res.users'].search([('id', '=', 2)]).company_id

        company.env['qbd.orderinvoice.logger'].search([]).unlink()
        company.check_tax_code_for_order_invoices()

        if not company.qb_default_tax:
            raise UserError(
                'Set Default Tax in Company -> QBD Account and Taxes Configuration -> Default Tax')

        if company.export_inv_limit:
            limit = int(company.export_inv_limit)
        elif self._context.get('is_vendor_bill'):
            limit = int(company.export_vendor_bill_limit)
        else:
            limit = 0

        if company.export_invoice_date:
            export_date = company.export_invoice_date
        elif self._context.get('is_vendor_bill'):
            export_date = company.export_vendor_bill_date
        else:
            export_date = False

        self.env.cr.execute(
            "SELECT odoo_id FROM qbd_orderinvoice_logger WHERE type='invoice'")
        result = self.env.cr.fetchall()
        invoice_data_list = []
        for rec in result:
            # print ("Rec ---------------------------- ",rec[0])
            invoice_data_list.append(int(rec[0]))
        # print (invoice_data_list)

        filters = [('id', 'not in', invoice_data_list),
                   ('state', 'in', ['posted'])]

        if export_date:
            export_date = fields.Datetime.from_string(export_date)
            # print("Before ------------------------------ ", type(export_date), export_date)
            export_date_start = datetime(
                export_date.year, export_date.month, export_date.day)
            # print ("After ------------------------------ ",type(export_date), export_date_start)
            export_date_end = export_date_start + \
                timedelta(hours=23, minutes=59, seconds=59)

        if self._context.get('is_vendor_bill'):
            filters.append(('move_type', '=', 'in_invoice'))
        else:
            filters.append((('move_type', '=', 'out_invoice')))

        if export_date:
            filters.append(('invoice_date', '=', export_date))

        if company.export_updated_record:
            filters.append(('quickbooks_id', '!=', False))
            filters.append(('is_updated', '=', True))
        else:
            filters.append(('quickbooks_id', '=', False))

        if invoice_lst:
            invoices = invoice_lst
        else:
            _logger.info("FILTER===>>>>>>>>>>>>>>>>{}".format(filters))
            invoices = self.search(filters, limit=limit)
            _logger.info("INVOICESS===>>>>>>>>>>>>>>>>>>>>{}".format(invoices))
        # print('filters  :::::::::::::::::::::::::::::::::: ', filters)
        # print('invoices :::::::::::::::::::::::::::::::::: ', invoices)

        invoice_data_list = []
        if invoices:
            for invoice in invoices:
                invoice_dict = {}
                if company.export_updated_record:
                    if self._context.get('is_vendor_bill'):
                        invoice_dict = self.get_invoice_dict(
                            invoice, company.export_updated_record, is_vendor_bill=True)
                    else:
                        invoice_dict = self.get_invoice_dict(
                            invoice, company.export_updated_record)
                else:
                    if self._context.get('is_vendor_bill'):
                        invoice_dict = self.get_invoice_dict(
                            invoice, is_vendor_bill=True)
                    else:
                        invoice_dict = self.get_invoice_dict(invoice)

                if invoice_dict:
                    invoice_data_list.append(invoice_dict)

        if invoice_data_list:
            # print('\n\nInvoice data : ', invoice_data_list)
            # print('\nTotal Invoices : ', len(invoice_data_list))

            company = self.env['res.users'].search([('id', '=', 2)]).company_id
            headers = {'content-type': "application/json"}
            data = invoice_data_list

            data = {'invoices_list': data}

            url = None

            _logger.info("DATA IS {}".format(data))
            response = requests.request('POST', company.url + '/export_invoices', data=json.dumps(data),
                                        headers=headers,
                                        verify=False)

            # print("Response Text", type(response.text), response.text)

            try:
                resp = ast.literal_eval(response.text)

                # print('Resp : ', resp)
                if isinstance(resp, dict):
                    if resp.get('Message'):
                        raise UserError(_('No Invoice Exported'))
                    if company.export_updated_record == False:
                        for res in resp.get('Data'):
                            if 'odoo_id' in res and res.get('odoo_id'):
                                inv_id = self.browse(int(res.get('odoo_id')))
                                if inv_id:
                                    inv_id.write({
                                        'quickbooks_id': res.get('quickbooks_id') if res.get('quickbooks_id') else False,
                                        'qbd_number': res.get('qbd_invoice_ref_no') if res.get('qbd_invoice_ref_no') else '',
                                    })
                            loger_dict.update({'operation': 'Export Invoice',
                                               'odoo_id': res.get('odoo_id'),
                                               'qbd_id': res.get('quickbooks_id'),
                                               'message': res.get('messgae')
                                               })
                            qbd_loger_id = self.env['qbd.loger'].create(loger_dict)
                            # company.write({'qbd_loger_id': [(4, qbd_loger_id.id)]})
                            date_parsed = parse(res.get('last_modified_date'))
                            if self._context.get('is_vendor_bill'):
                                company.write({
                                    'export_vendor_bill_date': date_parsed
                                })
                            else:
                                company.write({
                                    'export_invoice_date': date_parsed
                                })
                    else:
                        for res in resp.get('Data'):
                            if res.get('Message'):
                                raise UserError(_('No Invoice Exported'))
                            if 'odoo_id' in res and res.get('odoo_id'):
                                inv_id = self.browse(int(res.get('odoo_id')))
                                if inv_id:
                                    if res.get('messgae') == 'Successfully Updated':
                                        inv_id.write({'is_updated': False})

                            loger_dict.update({'operation': 'Export Invoice',
                                               'odoo_id': res.get('odoo_id'),
                                               'qbd_id': res.get('quickbooks_id'),
                                               'message': res.get('messgae')
                                               })
                            qbd_loger_id = self.env['qbd.loger'].create(loger_dict)
                            # company.write({'qbd_loger_id': [(4, qbd_loger_id.id)]})
                            date_parsed = parse(res.get('last_modified_date'))
                            if self._context.get('is_vendor_bill'):
                                company.write({
                                    'export_vendor_bill_date': date_parsed
                                })
                            else:
                                company.write({
                                    'export_invoice_date': date_parsed
                                })

                else:
                    raise UserError(
                        _("No Data in Response Check Quickbook Desktop Terminal"))
            except Exception as ex:
                _logger.error(str(ex))
                raise ValidationError(str(ex))
        return True

    def get_invoice_dict(self, invoice, export_updated_record=False, is_vendor_bill=False):
        invoice_dict = {}
        _logger.info("INVOICE===>>>>>>>>>>>>{}".format(invoice))
        company = self.env['res.users'].search([('id', '=', 2)]).company_id
        # default_tax_on_invoice = company.qb_default_tax.name
        if not invoice.qbd_tax:
            raise UserError("Set QBD Tax to Invoice")
        default_tax_on_invoice = invoice.qbd_tax.name
        # print ("Default Taxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx ",default_tax_on_invoice)

        if export_updated_record:
            invoice_dict.update({
                'invoice_order_qbd_id': invoice.quickbooks_id,
            })
        else:
            invoice_dict.update({
                'invoice_order_qbd_id': '',
            })

        invoice_dict['odoo_invoice_number'] = invoice.name if len(
            invoice.name) < 11 else invoice.id
        invoice_dict['default_tax_on_invoice'] = default_tax_on_invoice
        if is_vendor_bill:
            invoice_dict.update({'is_vendor_bill': True})

        invoice_dict.update({
            'odoo_id': invoice.id,
            # 'name': order.name,
            'qbd_memo': invoice.name if invoice.name else '',
            'partner_name': invoice.partner_id.quickbooks_id,
            'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d'),
            'lpo_no': invoice.lpo_no,
            'veh_or_w_bill': invoice.veh_or_w_bill,
            'etr_no': invoice.etr_no,
        })

        if invoice.invoice_line_ids:
            invoice_dict.update({
                'invoice_lines': self.get_invoice_lines(invoice)
            })
        if invoice_dict:
            return invoice_dict

    def get_invoice_lines(self, invoice):
        invoice_lines = []
        # print ("Invoice Iddddddddddddddddddddddddddddddddddd ---------------------- ", invoice.id)
        for line in invoice.invoice_line_ids:
            line_dict = {}

            # print ("Invoice Iddddddddddddddddddddddddddddddddddd ---------------------- ",invoice.id)
            description = line.name if line.name else ''
            bad_chars = [';', ':', '!', "*", "$", "'"]
            for i in bad_chars:
                description = description.replace(i, "")

            # print ("line.tax_ids[0].quickbooks_id=====================",line.tax_ids[0].quickbooks_id)
            if line.product_id:
                line_dict.update({
                    'payment_terms': invoice.partner_id.property_payment_term_id.name if invoice.partner_id.property_payment_term_id.quickbooks_id else '',
                    'ref_number': invoice.id,
                    'product_name': line.product_id.quickbooks_id if line.product_id else '',
                    'name': description,
                    'quantity': line.quantity if line.quantity else '',
                    'price_unit': line.price_unit if line.price_unit else '',
                    'tax_id': line.tax_ids[0].quickbooks_id if line.tax_ids else '',
                    'qbd_tax_code': line.qbd_tax_code.name if line.qbd_tax_code.name else '',
                    'price_subtotal': line.price_subtotal if line.price_subtotal else '',
                })

            if line_dict:
                invoice_lines.append(line_dict)

        if invoice_lines:
            return invoice_lines

    def export_invoice_to_qbd_server_action(self):
        '''
            This method gets invoked from a server action
            to export selected invoices to QBD
        '''
        # ENSURE IF ALL ARE VENDOR BILL OR ALL ARE INVOICES
        if all([x.move_type == 'in_invoice' for x in self]):
            self.export_invoices(invoice_lst=self, is_vendor_bill=True)
        elif all([x.move_type == 'out_invoice' for x in self]):
            self.export_invoices(invoice_lst=self, is_vendor_bill=False)
        else:
            raise UserError(
                'Selected records must be either all invoices or all bills')
