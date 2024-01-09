# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    s_agent = fields.Selection([
        ('parent', 'Agent'),
        ('child', 'Sub agent')
        ], string='Agent or Sub agent', default='parent',
                               tracking=True)
    driver = fields.Boolean(
        string='Driver', help='Contact is driver or not',
        tracking=True)
    guide = fields.Boolean(
        string='Guide', help='Contact is guide or not',
        tracking=True)
    tour_consultant = fields.Boolean(
        string='Tour Consultant', help='Contact is tour consultant or not',
        tracking=True)

    date_of_birth = fields.Date(string="Date of born")
    passport_no = fields.Char(string="Passport No")
    date_of_expire = fields.Date(string="Date of Expire")


    def name_get(self):
        result = []
        for partner in self:
            ref = '[%s]' % partner.ref if partner.ref else ''
            name = '%s %s' % (ref, partner.name)
            result.append((partner.id, name))
        return result
