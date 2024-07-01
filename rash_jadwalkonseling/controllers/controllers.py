# -*- coding: utf-8 -*-
from odoo import http

# class RashJadwalkonseling(http.Controller):
#     @http.route('/rash_jadwalkonseling/rash_jadwalkonseling/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rash_jadwalkonseling/rash_jadwalkonseling/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rash_jadwalkonseling.listing', {
#             'root': '/rash_jadwalkonseling/rash_jadwalkonseling',
#             'objects': http.request.env['rash_jadwalkonseling.rash_jadwalkonseling'].search([]),
#         })

#     @http.route('/rash_jadwalkonseling/rash_jadwalkonseling/objects/<model("rash_jadwalkonseling.rash_jadwalkonseling"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rash_jadwalkonseling.object', {
#             'object': obj
#         })