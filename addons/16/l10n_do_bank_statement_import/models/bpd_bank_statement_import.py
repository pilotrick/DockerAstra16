# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import base64
from datetime import datetime as dt
import calendar
from odoo import models

class InheritedAccountJournal(models.Model):
    _inherit = "account.journal"
    
    statement_import_type = fields.Selection(selection_add=[
        ('popular', 'Banco Popular')
    ])


class AccountBankStatementImport(models.TransientModel):
    _inherit = 'account.bank.statement.wizard'

    def _import_popular_statement(self, rec, statement_id):
        """
        Process data from txt and generate bank statement for Banco Popular
        :param rec: account.bank.statement.wizard record
        """

        # Convert binary data to latin1
        data = base64.b64decode(rec.data_file)
        with open('/tmp/statement.txt', 'w+') as w_file:
            w_file.write(data.decode('latin1'))

        with open('/tmp/statement.txt', 'r+') as r_file:

            account = r_file.readline().split(",")[0].lstrip('0')
            self._get_journal_id(account, statement_id)

        # Write statement lines

        statement_line = []
 
        with open('/tmp/statement.txt', 'r') as data:
            
            for line in data:
                
                amount = line.split(",")[3].lstrip('0')
                statement_line.append((0, 0, {
                    'date': dt.strptime(line.split(",")[1], "%d/%m/%Y").strftime("%Y-%m-%d"),
                    'partner_id': self._get_partner_id(line.split(",")[2]),
                    'payment_ref': line.split(",")[5],
                    'account_number': line.split(",")[2].lstrip('0') if len(line.split(",")[2].lstrip('0')) == 9 else '',
                    'amount': amount if line.split(",")[4] == 'CR' else str(float(amount) * -1) }))

            if statement_line:
                statement_id.line_ids.unlink()
                statement_id.write({'line_ids': statement_line})
