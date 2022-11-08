# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import html_translate


class ShImageHotspotInfo(models.Model):
    _name = "sh.image.hotpost.info"
    _description = "Hotpost Info"
    
    name = fields.Char('Name',required=True)
    active = fields.Boolean('Active',default=True)
    description = fields.Html('description',translate = html_translate)
    
    # method whcih redirect to frontend for design menu html structure
    def action_sh_design_popover(self, context=None):
        
        if not len(self.ids) == 1:
            raise UserError(_('You can only design only one mega menu at a time.'))

        url = '/sh_image_hotspot_snippet/design_popover?id=%d&enable_editor=1' % (self.id)
        return {
            'name': ('Edit Popover'),
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }