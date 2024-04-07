#  See LICENSE file for full copyright and licensing details.

import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_do_currency_interval_unit = fields.Selection(related="company_id.l10n_do_currency_interval_unit", readonly=False)
    l10n_do_currency_provider = fields.Many2one(related="company_id.l10n_do_currency_provider", readonly=False)
    l10n_do_currency_next_execution_date = fields.Date(related="company_id.l10n_do_currency_next_execution_date", readonly=False)
    currency_base = fields.Selection(related="company_id.currency_base", readonly=False)
    rate_offset = fields.Float(related="company_id.rate_offset", readonly=False)
    last_currency_sync_date = fields.Date(related="company_id.last_currency_sync_date", readonly=False)
    astra_login = fields.Char(
        related="company_id.astra_login",
        readonly=False
    )
    astra_password = fields.Char(
        related="company_id.astra_password",
        readonly=False
    )

    @api.onchange('l10n_do_currency_interval_unit')
    def onchange_l10n_do_currency_interval_unit(self):
        # as the onchange is called upon each opening of the settings, we avoid overwriting
        # the next execution date if it has been already set
        if self.company_id.l10n_do_currency_next_execution_date:
            return
        if self.l10n_do_currency_interval_unit == 'daily':
            next_update = relativedelta(days=+1)
        elif self.l10n_do_currency_interval_unit == 'weekly':
            next_update = relativedelta(weeks=+1)
        elif self.l10n_do_currency_interval_unit == 'monthly':
            next_update = relativedelta(months=+1)
        else:
            self.l10n_do_currency_next_execution_date = False
            return
        self.l10n_do_currency_next_execution_date = fields.Date.to_string(datetime.datetime.now() + next_update)

    def l10n_do_update_currency_rates(self):
        companies = self.env['res.company'].browse([record.company_id.id for record in self])

        if not companies.l10n_do_update_currency_rates():
            raise UserError(_('Unable to fetch currency from given API. '
                              'The service may be temporary down. Please try again in a moment.'))
        message = _("Tasa(s) Actualizada(s)!")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message' : message,
                'sticky' : True
            }
        }

    def l10n_do_update_banks(self):
        companies = self.env['res.company'].browse([record.company_id.id for record in self])
        if not companies.l10n_do_update_banks():
            raise UserError(_('Unable to fetch currency from given API. '
                              'The service may be temporary down. Please try again in a moment.'))
        message = _("Lista de Banco Actualizado, ya puedes seleccionar!")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message' : message,
                'sticky' : True
            }
        }
    
            
