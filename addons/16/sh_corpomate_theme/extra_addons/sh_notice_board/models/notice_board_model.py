# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import models, fields


class ShNbNoticeBoard(models.Model):
    _name = 'sh.nb.notice.board'
    _description = 'Notice board for display news on website'
    _order = 'id desc'

    # Get Default Website
    def default_website(self):
        company_id = self.env.company.id

        if self._context.get('default_company_id'):
            company_id = self._context.get('default_company_id')

        domain = [('company_id', '=', company_id)]
        return self.env['website'].search(domain, limit=1)

    name = fields.Char('Title', required=True)
    desc = fields.Text('Description')
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    website_id = fields.Many2one(
        'website',
        default=default_website
    )
