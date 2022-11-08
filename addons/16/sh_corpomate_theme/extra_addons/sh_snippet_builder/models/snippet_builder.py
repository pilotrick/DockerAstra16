# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

import base64
from lxml import etree, html
from odoo import api, fields, models, _, tools
import logging
from lxml import etree
from lxml import etree as ElementTree
from odoo.addons.http_routing.models.ir_http import slugify
from odoo.exceptions import ValidationError
from odoo.tools.view_validation import valid_view

_logger = logging.getLogger(__name__)


class View(models.Model):
    _inherit = 'ir.ui.view'

    @api.model
    def sh_snippet_builder_save_js_assets_snippet(self, arch, snippet_key):
        if arch:
            arch = bytes(arch, 'utf-8')
            arch = base64.b64encode(arch)

            attachment_obj = self.env['ir.attachment']
            url = '/sh_snippet_builder/static/src/js/' + snippet_key + '.js'
            name = snippet_key + '.js'

            attach = attachment_obj.search([
                ('url', '=', url)
            ], limit=1)

            if not attach:
                attachment_vals = {
                    'public': True,
                    'type': 'binary',
                    'url': url,
                    'name': name,
                    'mimetype': 'application/javascript',
                    'datas': arch,

                }
                attach = attachment_obj.create(attachment_vals)
            if attach:
                attach.write({
                    'datas': arch
                })
                # Create an asset with the new attachment
                ir_asset_obj = self.env['ir.asset']
                asset = ir_asset_obj.search([
                    ('path', '=', url),
                    ('bundle', '=', 'web.assets_frontend')
                ], limit=1)

                if not asset:
                    new_asset_vals = {
                        'path': url,
                        'bundle': 'web.assets_frontend',
                        'name': name,
                    }
                    asset = ir_asset_obj.create(new_asset_vals)

                return asset

    @api.model
    def sh_snippet_builder_save_snippet(self, name, arch, snippet_key):
        # html to xml to add '/' at the end of self closing tags like br, ...
        xml_arch = etree.tostring(html.fromstring(arch), encoding='utf-8')
        new_snippet_view_values = {
            'name': name,
            'key': snippet_key,
            'type': 'qweb',
            'arch': xml_arch,
        }
        new_snippet_view_values.update(self._snippet_save_view_values_hook())
        return self.create(new_snippet_view_values)


class sh_snippet_builder(models.Model):
    _name = "sh.snippet.builder"
    _description = "Snippet Builder"
    _order = "id desc"

    name = fields.Char(string="Name", required=True)
    html = fields.Text(string="HTML")
    css = fields.Text(string="CSS", default="<style></style>")
    js = fields.Text(string="JS", default="<script></script>")
    view_id = fields.Many2one(string="View", comodel_name="ir.ui.view")

    js_asset_view_id = fields.Many2one(
        string="JS Assets View", comodel_name="ir.asset")

    def action_noupdate_tmpl(self):
        ir_model_data_obj = self.env['ir.model.data'].sudo()

        search_rec = ir_model_data_obj.sudo().search([
            ('module', '=', 'sh_snippet_builder'),
            ('name', '=', 'sh_snippet_builder_snippets'),
        ], limit=1)

        if search_rec:
            vals = {
                'noupdate': True,
            }
            search_rec.sudo().write(vals)

    @api.model
    def create(self, vals):
        global_js_view_arch = vals.get("js", '')
        res = super(sh_snippet_builder, self).create(vals)
#         vals.pop("js")

        IrUiView = self.env["ir.ui.view"]
        name = "sh_snippet_builder_ud_tmpl_" + str(res.id)
        key = "sh_corpomate_theme." + name
        view_arch = """<?xml version="1.0"?>
        <t name="Snippet Builder %(id)s" t-name="sh_corpomate_theme.sh_snippet_builder_ud_tmpl_%(id)s">
            <section class="sh_snippet_builder_section_user_defined">        
        """ % {
            'id': res.id
        }
        if res.css:
            view_arch += res.css
        if res.html:
            view_arch += res.html
        view_arch += """
            </section>
        </t>
        """
        view = IrUiView.sh_snippet_builder_save_snippet(
            res.name, view_arch, key)
        res.write({
            'view_id': view.id,
        })

        # =========================================================================
        # Link custom snippet template in our website.snippets inherited template.
        # =========================================================================
        snippet_panel_view = IrUiView.sudo().search([
            ('key', '=', 'sh_corpomate_theme.sh_snippet_builder_snippets')
        ], order='id desc', limit=1)
        if snippet_panel_view and snippet_panel_view.arch:
            doc = etree.XML(snippet_panel_view.arch)
            for node in doc.xpath("//div[@class='o_panel_body']"):
                new_node = """
               <t t-snippet="%(key)s" 
               t-thumbnail="/sh_corpomate_theme/static/src/img/extra_addons/sh_snippet_builder/blocks/s_1.png"/> 
                """ % {
                    'key': key
                }
                new_node = ElementTree.fromstring(new_node)
                node.insert(1, new_node)
                break
            snippet_panel_view.arch = etree.tostring(doc, encoding='unicode')
        # =========================================================================
        # Link custom snippet template in our website.snippets inherited template.
        # =========================================================================

        # -------------------------------------------
        # Make Assets template for JS
        # -------------------------------------------
        name = "sh_snippet_builder_ud_tmpl_" + str(res.id)
        key = "sh_corpomate_theme." + name

        asset = IrUiView.sh_snippet_builder_save_js_assets_snippet(
            global_js_view_arch, key)
        res.write({
            'js_asset_view_id': asset.id
        })
        # -------------------------------------------
        # Make Assets template for JS
        # -------------------------------------------
        return res

    def write(self, vals):
        res = super(sh_snippet_builder, self).write(vals)
        IrUiView = self.env["ir.ui.view"]
        for rec in self:
            view_arch = """<?xml version="1.0"?>
            <t name="Snippet Builder %(id)s" t-name="sh_corpomate_theme.sh_snippet_builder_ud_tmpl_%(id)s">
                <section class="sh_snippet_builder_section_user_defined">
            """ % {
                'id': rec.id
            }
#             if rec.js:
#                 view_arch += rec.js
            if rec.css:
                view_arch += rec.css
            if rec.html:
                view_arch += rec.html

            view_arch += """
                </section>
            </t>
            """

            xml_arch = etree.tostring(
                html.fromstring(view_arch), encoding='utf-8')
            name = "sh_snippet_builder_ud_tmpl_" + str(rec.id)
            key = "sh_corpomate_theme." + name
            view = IrUiView.search([('key', '=', key)], limit=1)
            if view:
                view.sudo().write({
                    'arch': xml_arch
                })

            # -------------------------------------------
            # Write Assets template for JS
            # -------------------------------------------

            js = rec.js
            IrUiView.sh_snippet_builder_save_js_assets_snippet(js, key)

            # -------------------------------------------
            # Write Assets template for JS
            # -------------------------------------------

        return res

    def unlink(self):
        IrUiView = self.env["ir.ui.view"]
        for snippet_record in self:

            name = "sh_snippet_builder_ud_tmpl_" + str(snippet_record.id)
            key = "sh_corpomate_theme." + name
            # =========================================================================
            # Remove links in Snippet Panel View
            # =========================================================================
            snippet_panel_view = IrUiView.sudo().search([
                ('key', '=', 'sh_corpomate_theme.sh_snippet_builder_snippets')
            ], order='id desc', limit=1)
            if snippet_panel_view and snippet_panel_view.arch:
                doc = etree.XML(snippet_panel_view.arch)
                xpath = '//t[@t-snippet="' + key + '"]'
                for node in doc.xpath(xpath):
                    node.getparent().remove(node)
                snippet_panel_view.arch = etree.tostring(
                    doc, encoding='unicode')
            # =========================================================================
            # Remove links in Snippet Panel View
            # =========================================================================

            # =================================================
            # Remove ir ui view Qweb
            # =================================================
            if snippet_record.view_id:
                snippet_record.view_id.unlink()

            # =================================================
            # Remove ir ui view Qweb
            # =================================================

            # ----------------------------------------------------------------------------
            # Delete assets template.
            # ----------------------------------------------------------------------------
            if snippet_record.js_asset_view_id:
                url = snippet_record.js_asset_view_id.path or ''
                snippet_record.js_asset_view_id.unlink()
                # delete attachment also.
                attachment_obj = self.env['ir.attachment']

                attach = attachment_obj.search([
                    ('url', '=', url)
                ], limit=1)

                if attach:
                    attach.unlink()

            # ----------------------------------------------------------------------------
            # Delete assets template.
            # ----------------------------------------------------------------------------

        return super(sh_snippet_builder, self).unlink()
