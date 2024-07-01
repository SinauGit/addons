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
import logging
import functools

from urllib.parse import urlencode, quote_plus
from urllib.parse import urlparse, urlunparse, parse_qs
from werkzeug.exceptions import Unauthorized, Forbidden

from odoo import http, api, SUPERUSER_ID

from odoo.addons.muk_rest import validators, tools

_logger = logging.getLogger(__name__)

GRANT_RESPONSE_MAP = {
    'authorization_code': ['code'],
    'implicit': ['token'],
}

SAFE_URL_CHARS = set(
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ' 
    'abcdefghijklmnopqrstuvwxyz'
    '0123456789' '_.-' 
    '=&;:%+~,*@!()/?'
)

INVALID_HEX_PATTERN = re.compile(
    r'%[^0-9A-Fa-f]|%[0-9A-Fa-f][^0-9A-Fa-f]'
)

#----------------------------------------------------------
# Functions
#----------------------------------------------------------

def get_response_type(grant_type):
    return GRANT_RESPONSE_MAP.get(grant_type, [])

def clean_complex_query_params(query):
    cleaned_params = {}
    parsed_url = urlparse(query)
    params = parse_qs(parsed_url.query)
    for key, value in params.items():
        param_check = any(
            param and not set(param) <= SAFE_URL_CHARS or
            INVALID_HEX_PATTERN.search(param) 
            for param in value
        )
        if not param_check:
            cleaned_params[key] = value
    parsed_url = parsed_url._replace(query=urlencode(cleaned_params, True))
    return urlunparse(parsed_url)

def verify_oauth1_request(realms=[], raise_exception=False):
    try:
        valid, request = validators.oauth1_provider.validate_protected_resource_request(
            uri=clean_complex_query_params(http.request.httprequest.url),
            http_method=http.request.httprequest.method,
            body=http.request.httprequest.form,
            headers=http.request.httprequest.headers,
            realms=realms)
        return valid, request
    except Exception:
        if raise_exception:
            raise
        return False, None

def verify_oauth2_request(scopes=[], raise_exception=False):
    try:
        valid, request = validators.oauth2_provider.verify_request(
            uri=clean_complex_query_params(http.request.httprequest.url),
            http_method=http.request.httprequest.method,
            body=http.request.httprequest.form,
            headers=http.request.httprequest.headers,
            scopes=scopes)
        return valid, request
    except Exception:
        if raise_exception:
            raise
        return False, None
    
#----------------------------------------------------------
# Decorators
#----------------------------------------------------------

def protected(operations=['read'], check_custom_routes=False, *args, **kwargs):
    def wrapper(func):
        @functools.wraps(func)
        def verify(*args, **kwargs):
            model_param = http.request.params.get('model', None)
            model_request = model_param and [model_param] or []
            oauth1_verify = verify_oauth1_request(realms=model_request)
            oauth2_verify = verify_oauth2_request(scopes=model_request)
            valid, request = (False, False)
            if oauth1_verify[0]:
                valid, request = oauth1_verify
            elif oauth2_verify[0]:
                valid, request = oauth2_verify
            if not valid or not (request and request.access_token):
                raise Unauthorized()
            user = request.access_token.user
            if not user and request.access_token.oauth._name == 'muk_rest.oauth2':
                user = request.access_token.oauth.state == 'client_credentials' and request.access_token.oauth.user  
            env = user and api.Environment(http.request.cr, user.id, http.request.session.context or {})
            if not (user and env):
                raise Unauthorized()
            if check_custom_routes:
                domain = [('route', '=', http.request.httprequest.path)]
                route = env['muk_rest.endpoint'].search(domain, limit=1).exists()
                if route and route.perm_read and 'read' not in operations:
                    operations.append('read')
                if route and route.perm_write and 'write' not in operations:
                    operations.append('write')
                if route and route.perm_create and 'create' not in operations:
                    operations.append('create')
                if route and route.perm_unlink and 'unlink' not in operations:
                    operations.append('unlink')
            if model_param and request.access_token.oauth.security == 'advanced':
                rules = request.access_token.oauth.mapped('rules').filtered(lambda rec: rec.model.model == model_param)
                properties = rules.read(fields=["perm_%s" % operation for operation in operations])
                for operation in operations:
                    if not any([property.get("perm_%s" % operation, False) for property in properties]):
                        raise Forbidden()
            http.request._env = env
            http.request._uid = user.id
            if not http.request.session.session_token:
                sid = http.request.session.sid
                token = user._compute_session_token(sid)
                http.request.session.rotate = True
                http.request.session.uid = user.id
                http.request.session.login = user.login
                http.request.session.session_token = token
                http.request.session.get_context()
                http.request.disable_db = False
                http.request.uid = user.id
            kwargs.update({'token': request.access_token, 'oauth': request.access_token.oauth})
            kwargs.update({'custom': route if check_custom_routes else False}) 
            return func(*args, **kwargs)
        return verify
    return wrapper