#  See LICENSE file for full licensing details.

from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    rate = fields.Float(
        # Deprecated.
        # Do not forwardport to v14.
    )
