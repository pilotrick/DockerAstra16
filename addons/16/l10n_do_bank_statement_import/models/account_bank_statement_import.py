# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from calendar import month_name
import os


class AccountBankStatementImport(models.TransientModel):
    _inherit = 'account.bank.statement.wizard'

    def _validate_file_extension(self, filename, bank):
        """Depending on bank, validate uploaded file extension"""
        if bank == 'popular':
            return True if filename.endswith('.txt') else False
        elif bank == 'bhd':
            return True if filename.endswith('.csv') else False
        elif bank == 'scotiabank':
            return True if filename.endswith('.csv') else False
        elif bank == 'reserva':
            return True if filename.endswith('.csv') else False
        elif bank == 'manual':
            return True if filename.endswith('.csv') else False

    def _get_partner_id(self, account):
        """Returns given account partner_id, if exists"""
        bank_id = self.env['res.partner.bank'].search([
            ('acc_number', '=', account.lstrip('0'))])

        return bank_id.partner_id.id if bank_id.partner_id else False

    def _get_journal_id(self, account, statement_id):
        """Return journal if file bank account match journal bank account"""
        acc_number = statement_id.journal_id.bank_account_id.acc_number
        if account == acc_number:
            return True
        else:
            raise ValidationError(_('Error. Statement bank account doesn\'t '
                                    'match this journal account.'))
    
    # def _get_month_name(self, month_no):
    #     """Return Month Name"""
    #     locale = self.env.context.get('lang')
        
    #     if locale[:2] == 'es':
    #         meses = {
    #             1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    #             5: 'Mayo', 6: 'Junio', 7: 'Julio', 8:'Agosto',
    #             9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre',
    #             12: 'Diciembre'
    #         }
    #         return meses.get(month_no)

    #     else:
    #         return month_name[month_no]

    def import_dominican_statement(self):
        for rec in self:
            if rec.data_file:
                if self._validate_file_extension(rec.filename, rec.bank_st):
                    active_id = rec._context.get('active_ids')
                    bs_id = rec.env["account.bank.statement"].browse(active_id)
                    if rec.bank_st == 'popular':
                        self._import_popular_statement(rec, bs_id)
                    elif rec.bank_st == 'bhd':
                        self._import_bhd_statement(rec, bs_id)
                    elif rec.bank_st == 'scotiabank':
                        self._import_scotiabank_statement(rec, bs_id)
                    elif rec.bank_st == 'reserva':
                        self._import_reserva_statement(rec, bs_id)
                    elif rec.bank_st == 'manual':
                        self._import_manual_statement(rec, bs_id)

                else:
                    raise ValidationError(_('Error. Wrong file extension.'))
