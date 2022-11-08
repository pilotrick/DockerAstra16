# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api

class sh_corpomate_theme_testimonial(models.Model):
    _name = "sh.corpomate.theme.testimonial"
    _description = "Testimonial Front Theme Config"
    _order = "id desc"
    _rec_name='partner'
    
    comment = fields.Text(string = "Testimonial")
    name = fields.Char()    
    url_video = fields.Char(string = "Video URL")
    sequence = fields.Integer(string = "Sequence")
    active = fields.Boolean(string = "Active",default=True)
    partner = fields.Many2one(comodel_name="res.partner",string=" Name",required = True)
    sh_image = fields.Image(string = "Image")
    function = fields.Char(string = "Job Position")
    website_id = fields.Many2one('website')

    @api.onchange('partner')
    def _get_testimonial_image(self):   
        if self.partner:
            self.sh_image =  self.partner.image_1920 or False
            self.function = self.partner.function or False
        