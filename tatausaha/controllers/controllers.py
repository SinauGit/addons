# -*- coding: utf-8 -*-
# from odoo import http


# class Tatausaha(http.Controller):
#     @http.route('/tatausaha/tatausaha/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tatausaha/tatausaha/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tatausaha.listing', {
#             'root': '/tatausaha/tatausaha',
#             'objects': http.request.env['tatausaha.tatausaha'].search([]),
#         })

#     @http.route('/tatausaha/tatausaha/objects/<model("tatausaha.tatausaha"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tatausaha.object', {
#             'object': obj
#         })
