# # -*- coding: utf-8 -*-
# from odoo import http

# # class RashSiapbk(http.Controller):
# #     @http.route('/rash_siapbk/rash_siapbk/', auth='public')
# #     def index(self, **kw):
# #         return "Hello, world"

# #     @http.route('/rash_siapbk/rash_siapbk/objects/', auth='public')
# #     def list(self, **kw):
# #         return http.request.render('rash_siapbk.listing', {
# #             'root': '/rash_siapbk/rash_siapbk',
# #             'objects': http.request.env['rash_siapbk.rash_siapbk'].search([]),
# #         })

# #     @http.route('/rash_siapbk/rash_siapbk/objects/<model("rash_siapbk.rash_siapbk"):obj>/', auth='public')
# #     def object(self, obj, **kw):
# #         return http.request.render('rash_siapbk.object', {
# #             'object': obj
# #         })