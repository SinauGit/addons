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
import json
import base64
import urllib
import logging

from werkzeug import exceptions

from odoo import _, http, release
from odoo.http import request, Response
from odoo.models import check_method_name
from odoo.tools.image import image_data_uri
from odoo.tools import misc

from odoo.addons.muk_rest import validators, tools
from odoo.addons.muk_rest.tools.common import parse_value
from odoo.addons.muk_utils.tools.json import ResponseEncoder, RecordEncoder

_logger = logging.getLogger(__name__)

VERSION = {
    'server_version': release.version,
    'server_version_info': release.version_info,
    'server_serie': release.serie,
    'api_version': '3.5',
}

class RestfulController(http.Controller):
    
    #----------------------------------------------------------
    # Utility
    #----------------------------------------------------------
    
    @http.route('/api/<path:path>', auth="none", type='http', csrf=False)
    @tools.common.parse_exception
    def catch(self, **kw):    
        return exceptions.NotFound()
    
    @http.route('/api/custom/<path:path>', auth="none", type='http', csrf=False)
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected(operations=[], check_custom_routes=True)
    def custom(self, context=None, **kw):
        endpoint = kw.get('custom', False)
        if endpoint and endpoint.exists():
            ctx = request.session.context.copy()
            ctx.update(context and parse_value(context) or {})
            result = endpoint.with_context(ctx).evaluate(request.params)
            content = json.dumps(result, sort_keys=True, indent=4, cls=RecordEncoder)
            return Response(content, content_type='application/json;charset=utf-8', status=200)
        return exceptions.NotFound()
    
    #----------------------------------------------------------
    # Base
    #----------------------------------------------------------

    @http.route('/api', auth="none", type='http', methods=['GET'], csrf=False)
    @tools.common.parse_exception
    def version(self, **kw): 
        version = json.dumps(VERSION, sort_keys=True, indent=4)
        return Response(version, content_type='application/json;charset=utf-8', status=200)

    @http.route('/api/database', auth="none", type='http', methods=['GET'], csrf=False)
    @tools.common.parse_exception
    @tools.common.ensure_database
    def database(self, **kw): 
        result = {'database': request.session.db}
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)
    
    #----------------------------------------------------------
    # Session
    #----------------------------------------------------------
    
    @http.route('/api/user', auth="none", type='http', methods=['GET'], csrf=False)
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def user(self, **kw):
        result = {'uid': request.session.uid, 'name': request.env.user.name}
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200) 
    
    @http.route('/api/userinfo', auth="none", type='http', methods=['GET'], csrf=False)
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def userinfo(self, **kw):
        user = request.env.user
        uid = request.session.uid
        result = {
            'sub': uid,
            'name': user.name,
            'locale': user.lang,
            'zoneinfo': user.tz,
            'username': user.login,
            'email': user.partner_id.email,
            'website': user.partner_id.website,
            'phone_number': user.partner_id.phone,
            'address': {
                'formatted': user.partner_id.contact_address,
                'street_address': user.partner_id.street,
                'locality': user.partner_id.city,
                'postal_code': user.partner_id.zip,
                'region': user.partner_id.state_id.display_name,
                'country': user.partner_id.country_id.display_name,
            },
            'updated_at': user.partner_id.write_date,
            'picture': image_data_uri(user.partner_id.image_medium),
        }
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200) 
     
    @http.route('/api/session', auth="none", type='http', methods=['GET'], csrf=False)
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def session(self, **kw):
        user = request.env.user
        uid = request.session.uid
        result = {
            'uid': uid, 
            'name': user.name,
            'login': user.login,
            'display_name': user.partner_id.display_name,
            'is_system': user._is_system() if uid else False,
            'is_admin': user._is_admin() if uid else False,
            'context': request.session.get_context() if uid else {},   
            'partner_id': user.partner_id.id if uid and user.partner_id else None,       
            'currencies': request.env['ir.http'].get_currencies() if uid else {},          
            'company_id': user.company_id.id if uid else None,
            'companies': {
                'current_company': (user.company_id.id, user.company_id.name),
                'allowed_companies': [(company.id, company.name) for company in user.company_ids]
            } if user.has_group('base.group_multi_company') and len(user.company_ids) > 1 else False,
            'web.base.url': request.env['ir.config_parameter'].sudo().get_param('web.base.url', default=''),
            'db': request.session.db
        }
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200) 
    
    #----------------------------------------------------------
    # Generic Method
    #----------------------------------------------------------
    
    @http.route([
        '/api/call',
        '/api/call/<string:model>',
        '/api/call/<string:model>/<string:method>',
    ], auth="none", type='http', methods=['POST'], csrf=False)
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected(operations=['read', 'write', 'create', 'unlink'])
    def call(self, model, method, ids=None, context=None, args=None, kwargs=None, **kw):
        check_method_name(method)
        ctx = request.session.context.copy()
        ctx.update(context and parse_value(context) or {})
        ids = ids and parse_value(ids) or []
        args = args and parse_value(args) or []
        kwargs = kwargs and parse_value(kwargs) or {}
        records = request.env[model].with_context(ctx).browse(ids)
        result = getattr(records, method)(*args, **kwargs)
        content = json.dumps(result, sort_keys=True, indent=4, cls=RecordEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)
    
    @http.route([
        '/api/xmlid',
        '/api/xmlid/<string:xmlid>',
    ], auth="none", type='http', methods=['GET'], csrf=False)
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def xmlid(self, xmlid, **kw):
        record = request.env.ref(xmlid)
        result = {'model': record._name, 'id': record.id}
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200) 
    
    #----------------------------------------------------------
    # Files
    #----------------------------------------------------------
    
    @http.route([
        '/api/binary',        
        '/api/binary/<string:xmlid>',
        '/api/binary/<string:xmlid>/<string:filename>',
        '/api/binary/<int:id>',
        '/api/binary/<int:id>/<string:filename>',
        '/api/binary/<int:id>-<string:unique>',
        '/api/binary/<int:id>-<string:unique>/<string:filename>',
        '/api/binary/<int:id>-<string:unique>/<path:extra>/<string:filename>',
        '/api/binary/<string:model>/<int:id>/<string:field>',
        '/api/binary/<string:model>/<int:id>/<string:field>/<string:filename>'
    ], auth="none", type='http', methods=['GET'], csrf=False)
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def binary(self, xmlid=None, model='ir.attachment', id=None, field='datas', unique=None,
        filename=None, filename_field='datas_fname', mimetype=None, access_token=None,
        related_id=None, access_mode=None, file_response=False, **kw):
        status, headers, content = request.env['ir.http'].binary_content(xmlid=xmlid,
            model=model, id=id, field=field, unique=unique, filename=filename,
            filename_field=filename_field, mimetype=mimetype, related_id=related_id,
            access_mode=access_mode, access_token=access_token, download=True,
            default_mimetype='application/octet-stream')
        if status != 200:
            exceptions.abort(status)
        if file_response and misc.str2bool(file_response):
            decoded_content = base64.b64decode(content)
            headers.append(('Content-Length', len(decoded_content)))
            response = request.make_response(decoded_content, headers)
        else:
            if not filename:
                record = request.env.ref(xmlid, False) if xmlid else None
                if not record and id and model in request.env.registry:
                    record = request.env[model].browse(int(id))   
                if record and filename_field in record:
                    filename = record[filename_field]
                else:
                    filename = "%s-%s-%s" % (record._name, record.id, field)
            headers = dict(headers)
            result = {
                'content': content,
                'filename': filename,
                'content_disposition': headers.get('Content-Disposition'),
                'content_type': headers.get('Content-Type'),
                'content_length': len(base64.b64decode(content))}
            content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
            response = Response(content, content_type='application/json;charset=utf-8', status=200) 
        return response
    
    @http.route('/api/upload', auth="none", type='http', methods=['POST'], csrf=False)
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def upload(self, model, id, field=None, context=None, **kw):
        ctx = request.session.context.copy()
        ctx.update(context and parse_value(context) or {})
        files = request.httprequest.files.getlist('ufile')
        if field is not None and len(files) == 1:
            record = request.env[model].with_context(ctx).browse(int(id))
            result = record.write({field: base64.b64encode(files[0].read())})
        else:
            result = []
            for ufile in files:
                attachment = request.env['ir.attachment'].create({
                    'datas': base64.encodestring(ufile.read()),
                    'datas_fname': ufile.filename,
                    'name': ufile.filename,
                    'res_model': model,
                    'res_id': int(id),
                })
                result.append(attachment.id)
        content = json.dumps(result, sort_keys=True, indent=4, cls=RecordEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200) 
        
    #----------------------------------------------------------
    # Reports
    #----------------------------------------------------------
    
    @http.route([
        '/api/reports',
        '/api/reports/<string:name>',
        '/api/reports/<string:name>/<string:model>',
    ], auth="none", type='http', methods=['GET'], csrf=False)
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def reports(self, name=None, model=None, **kw):
        domain = []
        if name:
            domain.append(['name', 'ilike', name])
        if model:
            domain.append(['model', '=', model])
        result = request.env['ir.actions.report'].search_read(domain, ['name', 'model', 'report_name'])
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200) 
        
    @http.route([
        '/api/report',
        '/api/report/<string:report>',
        '/api/report/<string:report>/<string:type>',
    ], auth="none", type='http', methods=['GET'], csrf=False)
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def report(self, report, ids, type='PDF', context=None, options=None, file_response=False, **kw):
        ctx = request.session.context.copy()
        ctx.update(context and parse_value(context) or {})
        ids = ids and parse_value(ids) or []
        options = options and parse_value(options) or {}
        result = {'report': report, 'type': type}
        report = request.env['ir.actions.report']._get_report_from_name(report)
        if type.lower() == "html":
            data = report.with_context(ctx).render_qweb_html(ids, data=options)[0]
            result.update({
                'content': base64.b64encode(data),
                'content_type': 'text/html',
                'content_length': len(data)})
        elif type.lower() == "pdf":
            data = report.with_context(ctx).render_qweb_pdf(ids, data=options)[0]
            result.update({
                'content': base64.b64encode(data),
                'content_type': 'application/pdf',
                'content_length': len(data)})
        elif type.lower() == "text":
            data = report.with_context(ctx).render_qweb_text(ids, data=options)[0]
            result.update({
                'content': base64.b64encode(data),
                'content_type': 'text/plain',
                'content_length': len(data)})
        else:
            return exceptions.NotFound() 
        if file_response and misc.str2bool(file_response):
            headers = [
                ('Content-Type', result.get('content_type')),
                ('Content-Length',  result.get('content_length'))
            ]
            response = request.make_response(data, headers)
        else:
            content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
            response = Response(content, content_type='application/json;charset=utf-8', status=200) 
        return response
