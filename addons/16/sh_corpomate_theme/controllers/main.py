# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo.http import request
from odoo import http, fields, _
from odoo.exceptions import UserError
from odoo import http
from datetime import datetime
from odoo.tools.safe_eval import safe_eval

from odoo.addons.website.controllers.main import Website


from markupsafe import Markup


class Website(Website):

    @http.route()
    def theme_customize_data(self, is_view_data, enable=None, disable=None, reset_view_arch=False):
        TOTAL_THEME = 21
        TOTAL_THEME = TOTAL_THEME + 1
        # --------------------------------------
        # Footer Individual Change
        # --------------------------------------
        if len(enable) == 1 and any("sh_corpomate_theme.sh_corpomate_theme_footer_custom_" in s for s in enable):
            # whatever
            matching = [
                s for s in enable if "sh_corpomate_theme.sh_corpomate_theme_footer_custom_" in s]
            if matching and len(matching) == 1:
                matching_string = matching[0] or ''
                matching_theme_number = matching_string.replace(
                    'sh_corpomate_theme.sh_corpomate_theme_footer_custom_', '')
                if matching_theme_number:
                    i = 1
                    while i < TOTAL_THEME:
                        # Footer SCSS
                        asset = request.env.ref('sh_corpomate_theme.sh_corpomate_theme_style_footer_scss_%s' % (
                            i), raise_if_not_found=False)
                        if asset:
                            asset.write({'active': False})

                        i += 1
                    # Footer SCSS
                    to_active_asset = 'sh_corpomate_theme.sh_corpomate_theme_style_footer_scss_' + \
                        matching_theme_number
                    asset = request.env.ref(
                        to_active_asset, raise_if_not_found=False)
                    if asset:
                        asset.write({'active': True})


        if any("sh_corpomate_theme.sh_corpomate_theme_layout_readymade_" in s for s in enable):
            matching = [
                s for s in enable if "sh_corpomate_theme.sh_corpomate_theme_layout_readymade_" in s]
            if matching and len(matching) == 1:
                matching_string = matching[0] or ''
                matching_theme_number = matching_string.replace(
                    'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_', '')
                if matching_theme_number:
                    i = 1
                    while i < TOTAL_THEME:
                        # Header SCSS
                        asset = request.env.ref('sh_corpomate_theme.sh_corpomate_theme_style_header_scss_%s' % (
                            i), raise_if_not_found=False)
                        if asset:
                            asset.write({'active': False})
                        # Footer SCSS
                        asset = request.env.ref('sh_corpomate_theme.sh_corpomate_theme_style_footer_scss_%s' % (
                            i), raise_if_not_found=False)
                        if asset:
                            asset.write({'active': False})
                        # Color SCSS
                        asset = request.env.ref('sh_corpomate_theme.sh_corpomate_theme_primary_variable_color_scss_%s' % (
                            i), raise_if_not_found=False)
                        if asset:
                            #asset.write({'active': False})
                            query = """
                                UPDATE ir_asset
                                    SET active = false
                                WHERE id = %s;
                            """ % (asset.id)
                            request.env.cr.execute(query)                            
                        # Font SCSS
                        asset = request.env.ref('sh_corpomate_theme.sh_corpomate_theme_primary_variable_font_scss_%s' % (
                            i), raise_if_not_found=False)
                        if asset:
                            asset.write({'active': False})

                        i += 1

                    # Header SCSS
                    to_active_asset = 'sh_corpomate_theme.sh_corpomate_theme_style_header_scss_' + \
                        matching_theme_number
                    asset = request.env.ref(
                        to_active_asset, raise_if_not_found=False)
                    if asset:
                        asset.write({'active': True})
                    # Footer SCSS
                    to_active_asset = 'sh_corpomate_theme.sh_corpomate_theme_style_footer_scss_' + \
                        matching_theme_number
                    asset = request.env.ref(
                        to_active_asset, raise_if_not_found=False)
                    if asset:
                        asset.write({'active': True})
                    # Color SCSS
                    to_active_asset = 'sh_corpomate_theme.sh_corpomate_theme_primary_variable_color_scss_' + \
                        matching_theme_number
                    asset = request.env.ref(
                        to_active_asset, raise_if_not_found=False)
                    if asset:
                        #asset.write({'active': True})
                        query = """
                            UPDATE ir_asset
                                SET active = true
                            WHERE id = %s;
                        """ % (asset.id)
                        request.env.cr.execute(query)
                    # Font SCSS
                    to_active_asset = 'sh_corpomate_theme.sh_corpomate_theme_primary_variable_font_scss_' + \
                        matching_theme_number
                    asset = request.env.ref(
                        to_active_asset, raise_if_not_found=False)
                    if asset:
                        asset.write({'active': True})

        # ==============================================================
        # FOR READYMADE THEME
        # ==============================================================
        list_readymade_tmpl = [
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_1',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_2',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_3',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_4',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_5',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_6',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_7',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_8',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_9',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_10',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_11',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_12',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_13',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_14',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_15',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_16',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_17',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_18',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_19',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_20',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_21',
            'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_none',
        ]

        # ======================================================
        # STEP 1: CHECK IF CHANGED IN READYMADE THEME
        # ======================================================
        selected_readymade_tmpl = ''
        is_readymade_theme_changed = False
        for item in list_readymade_tmpl:
            if item in enable:
                selected_readymade_tmpl = item
                is_readymade_theme_changed = True
                break

#         multiwebsite_domain = [
#             ("website_id",'=', request.website.id),
#         ]

        multiwebsite_domain = request.website.website_domain()

        if is_readymade_theme_changed:

            # ======================================================
            # MANAGE LIST OF OUR PAGES VIEW KEY
            # ======================================================

            list_page_theme_1 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_1',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_1',
                'sh_corpomate_theme.sh_corpomate_tmpl_faq_1',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_1',
                'sh_corpomate_theme.sh_corpomate_tmpl_our_team_1',
                'sh_corpomate_theme.sh_corpomate_tmpl_privacy_policy_1',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_1',
                'sh_corpomate_theme.sh_corpomate_tmpl_terms_and_conditions_1',
                'sh_corpomate_theme.sh_corpomate_tmpl_mega_menu_1',
            ]
            list_page_theme_2 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_2',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_2',
                'sh_corpomate_theme.sh_corpomate_tmpl_faq_2',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_2',
                'sh_corpomate_theme.sh_corpomate_tmpl_our_team_2',
                'sh_corpomate_theme.sh_corpomate_tmpl_privacy_policy_2',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_2',
                'sh_corpomate_theme.sh_corpomate_tmpl_terms_and_conditions_2',
                'sh_corpomate_theme.sh_corpomate_tmpl_mega_menu_2',
            ]

            list_page_theme_3 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_3',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_3',
                'sh_corpomate_theme.sh_corpomate_tmpl_faq_3',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_3',
                'sh_corpomate_theme.sh_corpomate_tmpl_our_team_3',
                'sh_corpomate_theme.sh_corpomate_tmpl_privacy_policy_3',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_3',
                'sh_corpomate_theme.sh_corpomate_tmpl_terms_and_conditions_3',
                'sh_corpomate_theme.sh_corpomate_tmpl_mega_menu_3',
            ]

            list_page_theme_4 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_4',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_4',
                'sh_corpomate_theme.sh_corpomate_tmpl_faq_4',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_4',
                'sh_corpomate_theme.sh_corpomate_tmpl_our_team_4',
                'sh_corpomate_theme.sh_corpomate_tmpl_privacy_policy_4',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_4',
                'sh_corpomate_theme.sh_corpomate_tmpl_terms_and_conditions_4',
                'sh_corpomate_theme.sh_corpomate_tmpl_mega_menu_4',
            ]

            list_page_theme_5 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_5',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_5',
                'sh_corpomate_theme.sh_corpomate_tmpl_faq_5',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_5',
                'sh_corpomate_theme.sh_corpomate_tmpl_our_team_5',
                'sh_corpomate_theme.sh_corpomate_tmpl_privacy_policy_5',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_5',
                'sh_corpomate_theme.sh_corpomate_tmpl_terms_and_conditions_5',
                'sh_corpomate_theme.sh_corpomate_tmpl_mega_menu_5',
            ]

            list_page_theme_6 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_6',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_6',
                'sh_corpomate_theme.sh_corpomate_tmpl_faq_6',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_6',
                'sh_corpomate_theme.sh_corpomate_tmpl_our_team_6',
                'sh_corpomate_theme.sh_corpomate_tmpl_privacy_policy_6',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_6',
                'sh_corpomate_theme.sh_corpomate_tmpl_terms_and_conditions_6',
                'sh_corpomate_theme.sh_corpomate_tmpl_mega_menu_6',
            ]

            list_page_theme_7 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_7',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_7',
                'sh_corpomate_theme.sh_corpomate_tmpl_faq_7',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_7',
                'sh_corpomate_theme.sh_corpomate_tmpl_our_team_7',
                'sh_corpomate_theme.sh_corpomate_tmpl_privacy_policy_7',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_7',
                'sh_corpomate_theme.sh_corpomate_tmpl_terms_and_conditions_7',
                'sh_corpomate_theme.sh_corpomate_tmpl_mega_menu_7',
            ]

            list_page_theme_8 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_8',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_8',
                'sh_corpomate_theme.sh_corpomate_tmpl_faq_8',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_8',
                'sh_corpomate_theme.sh_corpomate_tmpl_our_team_8',
                'sh_corpomate_theme.sh_corpomate_tmpl_privacy_policy_8',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_8',
                'sh_corpomate_theme.sh_corpomate_tmpl_terms_and_conditions_8',
                'sh_corpomate_theme.sh_corpomate_tmpl_mega_menu_8',
            ]

            list_page_theme_9 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_9',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_9',
                'sh_corpomate_theme.sh_corpomate_tmpl_faq_9',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_9',
                'sh_corpomate_theme.sh_corpomate_tmpl_our_team_9',
                'sh_corpomate_theme.sh_corpomate_tmpl_privacy_policy_9',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_9',
                'sh_corpomate_theme.sh_corpomate_tmpl_terms_and_conditions_9',
                'sh_corpomate_theme.sh_corpomate_tmpl_mega_menu_9',
            ]

            list_page_theme_10 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_10',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_10',
                'sh_corpomate_theme.sh_corpomate_tmpl_faq_10',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_10',
                'sh_corpomate_theme.sh_corpomate_tmpl_our_team_10',
                'sh_corpomate_theme.sh_corpomate_tmpl_privacy_policy_10',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_10',
                'sh_corpomate_theme.sh_corpomate_tmpl_terms_and_conditions_10',
                'sh_corpomate_theme.sh_corpomate_tmpl_mega_menu_10',
            ]

            list_page_theme_11 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_11',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_11',
                'sh_corpomate_theme.sh_corpomate_tmpl_faq_11',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_11',
                #                 'sh_corpomate_theme.sh_corpomate_tmpl_our_team_11',
                'sh_corpomate_theme.sh_corpomate_tmpl_privacy_policy_11',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_11',
                'sh_corpomate_theme.sh_corpomate_tmpl_terms_and_conditions_11',
                'sh_corpomate_theme.sh_corpomate_tmpl_mega_menu_11',
            ]

            list_page_theme_12 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_12',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_12',
                'sh_corpomate_theme.sh_corpomate_tmpl_faq_12',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_12',
                'sh_corpomate_theme.sh_corpomate_tmpl_our_team_12',
                'sh_corpomate_theme.sh_corpomate_tmpl_privacy_policy_12',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_12',
                'sh_corpomate_theme.sh_corpomate_tmpl_terms_and_conditions_12',
                'sh_corpomate_theme.sh_corpomate_tmpl_project_12',
                'sh_corpomate_theme.sh_corpomate_tmpl_mega_menu_12',
            ]

            list_page_theme_13 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_13',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_13',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_13',
                'sh_corpomate_theme.sh_corpomate_tmpl_our_team_13',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_13',
            ]

            list_page_theme_14 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_14',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_14',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_14',
                'sh_corpomate_theme.sh_corpomate_tmpl_our_team_14',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_14',

            ]

            list_page_theme_15 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_15',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_15',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_15',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_15',
            ]

            list_page_theme_16 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_16',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_16',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_16',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_16',
            ]
            list_page_theme_17 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_17',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_17',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_17',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_17',
                'sh_corpomate_theme.sh_corpomate_tmpl_project_17',
                'sh_corpomate_theme.sh_corpomate_tmpl_gallery_17',
            ]
            list_page_theme_18 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_18',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_18',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_18',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_18',
                'sh_corpomate_theme.sh_corpomate_tmpl_portfolio_18',
                'sh_corpomate_theme.sh_corpomate_tmpl_our_team_18',
            ]

            list_page_theme_19 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_19',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_19',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_19',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_19',
                'sh_corpomate_theme.sh_corpomate_tmpl_statistics_19',
                'sh_corpomate_theme.sh_corpomate_tmpl_our_team_19',
            ]

            list_page_theme_20 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_20',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_20',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_20',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_20',
                # 'sh_corpomate_theme.sh_corpomate_tmpl_statistics_20',
                'sh_corpomate_theme.sh_corpomate_tmpl_our_team_20',
            ]


            list_page_theme_21 = [
                'sh_corpomate_theme.sh_corpomate_tmpl_about_us_21',
                'sh_corpomate_theme.sh_corpomate_tmpl_contact_us_21',
                'sh_corpomate_theme.sh_corpomate_tmpl_home_21',
                'sh_corpomate_theme.sh_corpomate_tmpl_service_21',
                'sh_corpomate_theme.sh_corpomate_tmpl_portfolio_21',
                'sh_corpomate_theme.sh_corpomate_tmpl_pricing_21',
                'sh_corpomate_theme.sh_corpomate_tmpl_event_21',
            ]

            theme_none_list_page = list_page_theme_1 + list_page_theme_2 + list_page_theme_3 + list_page_theme_4 + list_page_theme_5 + list_page_theme_6 + list_page_theme_7 + list_page_theme_8 + \
                list_page_theme_9 + list_page_theme_10 + list_page_theme_11 + list_page_theme_12 + \
                list_page_theme_13 + list_page_theme_14 + \
                list_page_theme_15 + list_page_theme_16 + list_page_theme_17 + list_page_theme_18 + list_page_theme_19 + list_page_theme_20 + list_page_theme_21


            dic_page_list = {
                'theme_1': list_page_theme_1,
                'theme_2': list_page_theme_2,
                'theme_3': list_page_theme_3,
                'theme_4': list_page_theme_4,
                'theme_5': list_page_theme_5,
                'theme_6': list_page_theme_6,
                'theme_7': list_page_theme_7,
                'theme_8': list_page_theme_8,
                'theme_9': list_page_theme_9,
                'theme_10': list_page_theme_10,
                'theme_11': list_page_theme_11,
                'theme_12': list_page_theme_12,
                'theme_13': list_page_theme_13,
                'theme_14': list_page_theme_14,
                'theme_15': list_page_theme_15,
                'theme_16': list_page_theme_16,
                'theme_17': list_page_theme_17,
                'theme_18': list_page_theme_18,
                'theme_19': list_page_theme_19,
                'theme_20': list_page_theme_20,
                'theme_21': list_page_theme_21,
                'theme_none': theme_none_list_page
            }

            # FIND VIEW IDS FOR ALL THEME AND MAKE DICTIONARY
            dic_page_view_ids_list = {}
            for key, value in dic_page_list.items():
                list_view_ids = []
                view_pages = request.env['ir.ui.view'].sudo().search([
                    ('key', 'in', value)
                ])
                if view_pages.sudo():
                    list_view_ids = view_pages.sudo().ids

                dic_page_view_ids_list.update({
                    key: list_view_ids
                })

            if dic_page_view_ids_list:

                # ======================================================
                # STEP 2 HIDE OUR ALL PAGES
                # ======================================================
                ids = sum(dic_page_view_ids_list.values(), [])
                page_domain = [('view_id', 'in', ids)]

                # UNPUBLISH ALL OUR PAGES.
                pages = request.env['website.page'].sudo().search(
                    page_domain + multiwebsite_domain)
                              
                if pages:
                    #                     pages.sudo().write({
                    #                         'website_published': False,
                    #                         })

                    # delete all menu here
                    menu_ids_list = []
                    for page in pages:
                        if page.menu_ids:
                            menu_ids_list += page.menu_ids.ids

                    menu_domain = [
                        ('id', 'in', menu_ids_list),
                        ("website_id", '=', request.website.id),
                    ]
                    menus = request.env['website.menu'].sudo().search(
                        menu_domain)

                    if menus:
                        menus.sudo().unlink()

                
                # delete all menu here
                # ======================================================
                # STEP 2 HIDE OUR ALL PAGES
                # ======================================================

                # ======================================================
                # STEP 3 SHOW SELECTED THEME PAGES
                # ======================================================

                if selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_1':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_1", []))]

                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_2':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_2", []))]

                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_3':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_3", []))]

                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_4':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_4", []))]

                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_5':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_5", []))]

                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_6':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_6", []))]

                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_7':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_7", []))]

                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_8':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_8", []))]

                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_9':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_9", []))]

                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_10':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_10", []))]

                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_11':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_11", []))]

                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_12':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_12", []))]

                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_13':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_13", []))]

                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_14':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_14", []))]

                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_15':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_15", []))]

                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_16':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_16", []))]

                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_17':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_17", []))]

                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_18':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_18", []))]

                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_19':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_19", []))]
                
                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_20':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_20", []))] 

                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_21':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_21", []))]                                                
                                    

                elif selected_readymade_tmpl == 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_none':
                    page_domain = [
                        ('view_id', 'in', dic_page_view_ids_list.get("theme_none", []))]

                    theme_none_domain = [
                        ('view_id.key', '=', 'website.homepage'),
                        ('website_id', '=', request.website.id),
                    ]

                    page_home = request.env['website.page'].sudo().search(
                        theme_none_domain)
                    if page_home:
                        page_home.sudo().is_homepage = True

                # PUBLISH SPECIFIED THEME PAGES.
                pages = request.env['website.page'].sudo().search(
                    page_domain + multiwebsite_domain)
                

                if pages and selected_readymade_tmpl != 'sh_corpomate_theme.sh_corpomate_theme_layout_readymade_none':

                    #                     pages.sudo().write({
                    #                         'website_published': True,
                    #                         })

                    # Create Menu Here
                    for page in pages:
                        menu_vals = {
                            'page_id': page.id,
                            'name': page.name,
                            'url': page.url,
                            'parent_id': request.website.menu_id.id,
                            'website_id': request.website.id,
                        }

                        # search menu
                        domain = [
                            ('website_id', '=', request.website.id),
                            ('page_id', '=', page.id),
                            ('url', '=', page.url),
                        ]

                        search_menu = request.env['website.menu'].sudo().search(
                            domain)
                        if not search_menu:

                            # search menu
                            domain = [
                                ('website_id', '=', False),
                                ('page_id', '=', page.id),
                                ('url', '=', page.url),
                            ]
                            search_menu = request.env['website.menu'].sudo().search(
                                domain, limit=1)

                            if search_menu:
                                # TODO: ADD HOMEPAGE AND SEQUENCE IN BELOW DICTIONARY.

                                menu_vals.update({
                                    "sh_website_mega_menu_html": search_menu.sh_website_mega_menu_html,
                                    "sequence": search_menu.sequence,
                                })
                          
                            menus = request.env['website.menu'].sudo().create(
                                menu_vals)

                            # ========================
                            # Make Home Page Here

                            if page.view_id and 'sh_corpomate_theme.sh_corpomate_tmpl_home_' in page.view_id.key:
                                page.sudo().is_homepage = True

                    # Create Menu Here

                # ======================================================
                # STEP 3 SHOW SELECTED THEME PAGES
                # ======================================================

        # ==============================================================
        # FOR READYMADE THEME
        # ==============================================================

        response = super(Website, self).theme_customize_data(is_view_data, enable, disable, reset_view_arch)

        return response


class main(http.Controller):

    @http.route('/sh_corpomate_theme/render_testimonial', type='json', auth="none", methods=['post'], website=True)
    def render_testimonial(self, template_id=False):
        print('\n\n\n\n template_id',template_id)
        domain_testimonial = [
            ('active', '=', True),
            ('website_id', 'in', (False, request.website.id))
        ]

        testimonial_order = "sequence desc"

        testimonials = request.env['sh.corpomate.theme.testimonial'].sudo().search(
            domain_testimonial,
            order=testimonial_order,
        )

        data = Markup('<div class="owl-carousel owl-theme">')
        if testimonials:
            for testimonial in testimonials:
                data += request.env["ir.ui.view"]._render_template(template_id, values={
                    'testimonial': testimonial,
                })
        data = data + Markup('</div>')
        return data

    @http.route('/sh_corpomate_theme/render_our_partner', type='json', auth="none", methods=['post'], website=True)
    def render_our_partner(self, template_id=False):

        domain_our_partner = [
            ('active', '=', True),
        ]

        our_partner_order = "sequence desc"

        our_partners = request.env['sh.corpomate.theme.our.partner'].sudo().search(
            domain_our_partner,
            order=our_partner_order,
        )

        data = Markup('<div class="owl-carousel owl-theme carousel-main">')
        if our_partners:
            for our_partner in our_partners:
                data += request.env["ir.ui.view"]._render_template(template_id, values={
                    'our_partner': our_partner,
                })
        data = data + Markup('</div>')
        return data
