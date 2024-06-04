# -*- coding: utf-8 -*-
from odoo import http

# class RashKesiswaan(http.Controller):
#     @http.route('/rash_kesiswaan/rash_kesiswaan/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rash_kesiswaan/rash_kesiswaan/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rash_kesiswaan.listing', {
#             'root': '/rash_kesiswaan/rash_kesiswaan',
#             'objects': http.request.env['rash_kesiswaan.rash_kesiswaan'].search([]),
#         })

#     @http.route('/rash_kesiswaan/rash_kesiswaan/objects/<model("rash_kesiswaan.rash_kesiswaan"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rash_kesiswaan.object', {
#             'object': obj
#         })