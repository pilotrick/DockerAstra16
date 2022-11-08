from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    allow_print_statement_portal = fields.Boolean(
        'Permitir estados por pagina web?',
    )
