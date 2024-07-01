# -*- coding: utf-8 -*-
from odoo import http

# class FloatNumberDiscount(http.Controller):
#     @http.route('/float_number_discount/float_number_discount/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/float_number_discount/float_number_discount/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('float_number_discount.listing', {
#             'root': '/float_number_discount/float_number_discount',
#             'objects': http.request.env['float_number_discount.float_number_discount'].search([]),
#         })

#     @http.route('/float_number_discount/float_number_discount/objects/<model("float_number_discount.float_number_discount"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('float_number_discount.object', {
#             'object': obj
#         })