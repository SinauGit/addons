###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK REST API for Odoo 
#    (see https://mukit.at).
#
#    MuK Proprietary License v1.0
#
#    This software and associated files (the "Software") may only be used 
#    (executed, modified, executed after modifications) if you have
#    purchased a valid license from MuK IT GmbH.
#
#    The above permissions are granted for a single database per purchased 
#    license. Furthermore, with a valid license it is permitted to use the
#    software on other databases as long as the usage is limited to a testing
#    or development environment.
#
#    You may develop modules based on the Software or that use the Software
#    as a library (typically by depending on it, importing it and using its
#    resources), but without copying any source code or material from the
#    Software. You may distribute those modules under the license of your
#    choice, provided that this license is compatible with the terms of the 
#    MuK Proprietary License (For example: LGPL, MIT, or proprietary licenses
#    similar to this one).
#
#    It is forbidden to publish, distribute, sublicense, or sell copies of
#    the Software or modified copies of the Software.
#
#    The above copyright notice and this permission notice must be included
#    in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###################################################################################

import re
import ast
import json
import urllib
import logging

from werkzeug import exceptions

from odoo import _, http, release
from odoo.http import request, Response
from odoo.exceptions import AccessError, UserError

from odoo.addons.muk_rest import validators, tools
from odoo.addons.muk_rest.tools.common import parse_value
from odoo.addons.muk_utils.tools.json import ResponseEncoder, RecordEncoder

_logger = logging.getLogger(__name__)

class SecurityController(http.Controller):

    #----------------------------------------------------------
    # Access
    #----------------------------------------------------------
    
    @http.route([
        '/api/access/rights',
        '/api/access/rights/<string:model>',
        '/api/access/rights/<string:model>/<string:operation>',
    ], auth="none", type='http', methods=['GET'],  csrf=False)
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def access_rights(self, model, operation='read', **kw):
        try:
            result = request.env[model].check_access_rights(operation)
        except (AccessError, UserError):
            result = False
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)
    
    @http.route([
        '/api/access/rules',
        '/api/access/rules/<string:model>',
        '/api/access/rules/<string:model>/<string:operation>',
    ], auth="none", type='http', methods=['GET'],  csrf=False)
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def access_rules(self, model, ids, operation='read', **kw):
        ids = ids and parse_value(ids) or []
        try:
            result = request.env[model].browse(ids).check_access_rule(operation) is None
        except (AccessError, UserError):
            result = False
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)
    
    @http.route([
        '/api/access/fields',
        '/api/access/fields/<string:model>',
        '/api/access/fields/<string:model>/<string:operation>',
    ], auth="none", type='http', methods=['GET'],  csrf=False)
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def access_fields(self, model, operation='read', fields=None, **kw):
        fields = fields and parse_value(fields) or None
        try:
            result = request.env[model].check_field_access_rights(operation, fields=fields)
        except (AccessError, UserError):
            result = False
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)
    
    @http.route([
        '/api/access',
        '/api/access/<string:model>',
        '/api/access/<string:model>/<string:operation>',
    ], auth="none", type='http', methods=['GET'],  csrf=False)
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def access(self, model, ids, operation='read', fields=None, **kw):
        ids = ids and parse_value(ids) or []
        fields = fields and parse_value(fields) or None
        try:
            rights = request.env[model].check_access_rights(operation)
            rules = request.env[model].browse(ids).check_access_rule(operation) is None
            fields = request.env[model].check_field_access_rights(operation, fields=fields)
            result = rights and rules and bool(fields)
        except (AccessError, UserError):
            raise
            result = False
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)