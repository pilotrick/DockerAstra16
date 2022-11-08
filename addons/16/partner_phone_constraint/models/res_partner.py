# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.constrains('phone', 'mobile')
    def _check_number_format(self):
        if self.phone and not self.phone.isdigit():
            raise ValidationError(_('Attention !! Phone number %s , should contains only numbers ' % (self.phone)))
        if self.mobile and not self.mobile.isdigit():
            raise ValidationError(_('Attention !! Mobile number %s , should contains only numbers ' % (self.mobile)))