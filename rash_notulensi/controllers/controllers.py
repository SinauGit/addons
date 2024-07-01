# -*- coding: utf-8 -*-
from odoo import http

# class RashNotulensi(http.Controller):
#     @http.route('/rash_notulensi/rash_notulensi/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rash_notulensi/rash_notulensi/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rash_notulensi.listing', {
#             'root': '/rash_notulensi/rash_notulensi',
#             'objects': http.request.env['rash_notulensi.rash_notulensi'].search([]),
#         })

#     @http.route('/rash_notulensi/rash_notulensi/objects/<model("rash_notulensi.rash_notulensi"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rash_notulensi.object', {
#             'object': obj
#         })