# -*- coding: utf-8 -*-
# from odoo import http


# class TassSales(http.Controller):
#     @http.route('/tass_sales/tass_sales/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tass_sales/tass_sales/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tass_sales.listing', {
#             'root': '/tass_sales/tass_sales',
#             'objects': http.request.env['tass_sales.tass_sales'].search([]),
#         })

#     @http.route('/tass_sales/tass_sales/objects/<model("tass_sales.tass_sales"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tass_sales.object', {
#             'object': obj
#         })
