# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import Controller, request, route

class CustomController(http.Controller):
    
    @http.route('/sh_image_hotspot_info', auth='user', type='json', website=True)
    def image_hotspot_info(self, styleOption):
        domain = [('active','=',True),('id','=',styleOption)]
        HotspotInfoObj = request.env['sh.image.hotpost.info']
        style_rec = HotspotInfoObj.search(domain,limit=1)
        html = style_rec.description
        return {
            'html':html,
        }
    
    @http.route('/sh_image_hotspot_snippet/design_popover', type='http', auth="user", website=True)
    def design_popover(self, id = False, **kw):
            
            if id and type(id) != int:
                id = int(id)
            
            record = False
            if id:
                record = request.env["sh.image.hotpost.info"].browse(id)
            
            values = {
                'record': record,
            }
            return request.render("sh_corpomate_theme.sh_website_megamenu_design_popover_tmpl",values)
           