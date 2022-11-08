# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BottomNavigationBar(models.Model):
    _inherit = ['website.published.multi.mixin']
    _name = 'sh.bottom.navigation.bar'
    _description = "Bottom Navigation Bar"
    _order = 'id desc'

    name = fields.Char(string="Name", required=True)
    nav_line = fields.One2many('sh.bottom.navigation.bar.line',
                               'bottom_navigation_bar_id', string='Nav Lines', copy=True, auto_join=True)
    style_type = fields.Selection([
        # ('style_1', 'Style 1'),
        ('style_2', 'Style 1'),
        ('style_3', 'Style 2'),
    ], string="Style", required=True)

    font_boolean = fields.Boolean('Is show text?')





class BottomNavigationBarLine(models.Model):
    _name = 'sh.bottom.navigation.bar.line'
    _description = 'Bottom Navigation Bar Lines'
    _order = 'sequence asc'

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer('Sequence', default=0, index=True, required=True)
    icon = fields.Char(string="Icon")
    url = fields.Char(string="URL")
    type = fields.Selection([
        ('home', 'Home'),
        ('lang', 'Language'),
        ('custom', 'Custom'),
    ], string="Trigger action", required=True)

    bottom_navigation_bar_id = fields.Many2one(
        'sh.bottom.navigation.bar', string='Navigation Bar Reference', required=True, ondelete='cascade', index=True, copy=False)

    # @api.model
    # def create(self, vals):
    #     res = super(BottomNavigationBarLine, self).create(vals)
    #     if res.bottom_navigation_bar_id:
    #         lines = self.search([
    #             ('bottom_navigation_bar_id', '=', res.bottom_navigation_bar_id.id)
    #         ])
    #         if len(lines.ids) > 5:
    #             raise UserError(
    #                 _('You can add maximam 5 lines.')
    #             )
    #     return res


