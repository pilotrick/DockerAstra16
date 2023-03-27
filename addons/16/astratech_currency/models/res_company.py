#  See LICENSE file for full licensing details.

import json
import logging
import requests
import pytz
from dateutil.relativedelta import relativedelta
import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

CURRENCY_AVAILABLE = ['EUR', 'USD']


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_do_currency_interval_unit = fields.Selection(
        [
            ('manually', 'Manually'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='daily',
        string='Currency Interval',
    )
    l10n_do_currency_provider = fields.Many2one('astra.api.banks', string='Bank')
    currency_base = fields.Selection(
        [('purchase_rate', 'Buy rate'), ('sale_rate', 'Sell rate')], default='sale_rate'
    )
    rate_offset = fields.Float('Offset', default=0)
    l10n_do_currency_next_execution_date = fields.Date(
        string="Following Execution Date"
    )
    last_currency_sync_date = fields.Date(string="Last Sync Date", readonly=True)
    astra_login = fields.Char(
        string='Usuario',
    )
    astra_password = fields.Char(
        string='Password',
    )

    def _get_token_astra_api(self, company):
        api_url = (
            self.env['ir.config_parameter'].sudo().get_param('astratech.api.token')
        )
        params = {
            'username': company.astra_login,
            'password': company.astra_password,
            'rnc': company.vat,
        }
        if not company.astra_login or not company.astra_password:
            raise UserError(_('Usuarios y Password son Necesarios'))
        try:
            response = requests.get(api_url, params)
        except requests.exceptions.ConnectionError as e:
            raise UserError(_('API requests return the following error %s' % e))
        if response.status_code == 401:
            raise UserError(_('Usted no tiene Autorizacion a esta Api, Contacte a su Administrador '))
       
        d = {}
        token = ""
        try:
            d = json.loads(response.text)
        except TypeError:
            raise UserError(_('No serializable data from API response'))
        if 'x_astra_access_token' in d:
            token = d['x_astra_access_token']
        return token

    def l10n_do_update_currency_rates(self):

        all_good = True
        res = True
        for company in self:
            tz = pytz.timezone('America/Santo_Domingo')
            today = datetime.datetime.now(tz).date()
            date = self.l10n_do_currency_next_execution_date or today
            if date > today:
                raise UserError(_('Le Fecha de Ejecucion no puede ser mayor al dia de hoy'))
            
            if not company.l10n_do_currency_provider:
                raise UserError(_('Seleccione su banco de preferencia, Dar click al Icono de Banco'))
            
            if company.l10n_do_currency_provider:
                _logger.info("Calling API rates resource.")
                token = self._get_token_astra_api(company)
                api_url = (
                    self.env['ir.config_parameter']
                    .sudo()
                    .get_param('astratech.api.currency')
                )
                headers = {'x-astra-access-token': token}
                Rate = self.env['res.currency.rate']
                tasa = 0
                for curr in CURRENCY_AVAILABLE:
                    
                    try:
                        params = {
                            'date': date,
                            'bank_code': company.l10n_do_currency_provider.bank_code,
                            'currency': curr,
                        }
                        response = requests.get(api_url, params, headers=headers)
                    except requests.exceptions.ConnectionError as e:
                        raise UserError(_('API requests return the following error %s' % e))
                    
                    if response.status_code == 200:
                        rates = response.text
                        d = {}
                        try:
                            d = json.loads(rates)
                            data = d.get('banks')
                            for key, value in data.items():
                                tasa = float(value.get(company.currency_base)) + company.rate_offset
                        except TypeError:
                            raise UserError(_('No serializable data from API response'))
                    
                    currency_id = self.env.ref('base.' + curr)
                    if currency_id and currency_id.active:
                        rate_id = Rate.search(
                            [
                                ('name', '=', date),
                                ('currency_id', '=', currency_id.id),
                                ('company_id', '=', company.id),
                            ]
                        )
                        if rate_id:
                            rate_id.write({'inverse_company_rate': tasa})
                        else:
                            Rate.create(
                                {
                                    'name': date,
                                    'currency_id': currency_id.id,
                                    'inverse_company_rate': tasa,
                                    'company_id': company.id,
                                }
                            )

                company.last_currency_sync_date = today
            else:
                res = False
            if not res:
                all_good = False
                _logger.warning(_('Unable to fetch new rates records from API'))
        return all_good

    def l10n_do_update_banks(self):
        all_good = True
        token = False
        for company in self:
            if not token:
                token = self._get_token_astra_api(company)
            headers = {'x-astra-access-token': token}

            api_url = (
                self.env['ir.config_parameter']
                .sudo()
                .get_param('astratech.api.currency.banks')
            )
            try:
                response = requests.get(api_url, headers=headers)
            except requests.exceptions.ConnectionError as e:
                
                raise UserError(_('API requests return the following error %s' % e))

            if response.status_code == 200:
                rates_dict = response.text
                d = {}
                try:
                    d = json.loads(rates_dict)
                    data = d.get('banks')
                    bank = self.env['astra.api.banks']
                    for key, value in data.items():
                        bank = bank.search([(
                            "bank_code", '=', value.get("bank_code")
                        )])
                        
                        if not bank:
                            bank.create({
                                "name": value.get("name"),
                                "bank_code" : value.get("bank_code")
                            })
                except TypeError:
                    raise UserError(_('No serializable data from API response'))
        return all_good

    @api.model
    def l10n_do_run_update_currency(self):

        records = self.search([])
        if records:
            to_update = self.env['res.company']

            for record in records:
                if record.l10n_do_currency_interval_unit == 'daily':
                    next_update = relativedelta(days=+1)
                elif record.l10n_do_currency_interval_unit == 'weekly':
                    next_update = relativedelta(weeks=+1)
                elif record.l10n_do_currency_interval_unit == 'monthly':
                    next_update = relativedelta(months=+1)
                else:
                    record.l10n_do_currency_interval_unit = False
                    continue
                tz = pytz.timezone('America/Santo_Domingo')
                today = datetime.datetime.now(tz).date()
                record.l10n_do_currency_next_execution_date = today + next_update
                to_update += record
            to_update.l10n_do_update_currency_rates()
