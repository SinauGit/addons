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
import datetime

from oauthlib.oauth2 import RequestValidator
from oauthlib.oauth2 import InvalidRequestFatalError

from odoo import http
from odoo.tools.misc import consteq

from odoo.addons.muk_rest.tools import security
from odoo.addons.muk_utils.tools.http import decode_http_basic_authentication

_logger = logging.getLogger(__name__)

class OAuth2RequestValidator(RequestValidator):
    
    #----------------------------------------------------------
    # Configuration
    #----------------------------------------------------------
    
    def client_authentication_required(self, request, *args, **kwargs):
        if request.grant_type in ('password', 'authorization_code', 'refresh_token'):
            request = self.ensure_client_parameters(request)
            if request.client_id and self.get_client(request.client_id):
                return True
        return False
    
    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    def ensure_client_parameters(self, request):
        if not request.client_id:
            authorization_header = request.headers.get('Authorization')
            username, password = decode_http_basic_authentication(authorization_header)
            request.client_id = username
            request.client_secret = password
        if not request.client_id:
            raise InvalidRequestFatalError(description='Missing client_id parameter.', request=request)
        return request
    
    #----------------------------------------------------------
    # Validate
    #----------------------------------------------------------
    
    def validate_client_id(self, client_id, request, *args, **kwargs):
        if not request.client:
            request.client = self.get_client(client_id)
        return bool(request.client)

    def validate_redirect_uri(self, client_id, redirect_uri, request):
        if not request.client:
            request.client = self.get_client(client_id)
        if not request.client:
            return False
        request.redirect_uri = redirect_uri
        return redirect_uri in request.client.callbacks.mapped('url')

    def validate_response_type(self, client_id, response_type, client, request, *args, **kwargs):
        if not request.client:
            request.client = self.get_client(client_id)
        if not request.client:
            return False
        request.response_type = response_type
        return response_type in security.get_response_type(request.client.state)

    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        if client and client.security == 'advanced': 
            return set(client.mapped('rules.model.model')).issuperset(set(scopes))
        return True
    
    def validate_user(self, username, password, client, request, *args, **kwargs):
        request.user = http.request.session.authenticate(http.request.session.db, username, password)
        return bool(request.user)

    def validate_grant_type(self, client_id, grant_type, client, request, *args, **kwargs):
        if not request.client:
            request.client = self.get_client(client_id)
        return grant_type == 'refresh_token' or grant_type == request.client.state

    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        if not request.client:
            request.client = self.get_client(client_id)
        authorization_code = self.get_authorization_code(code)
        if authorization_code and consteq(authorization_code.oauth.client_id, request.client.client_id):
            request.user = authorization_code.user.id
            return True
        return False

    def invalidate_authorization_code(self, client_id, code, request, *args, **kwargs):
        authorization_code = self.get_authorization_code(code)
        if authorization_code and consteq(authorization_code.oauth.client_id, client_id):
            authorization_code.unlink()

    def validate_bearer_token(self, token, scopes, request):
        if not request.access_token:
            request.access_token = self.get_bearer_token(token)
        if not request.access_token:
            return False
        if request.access_token and request.access_token.oauth.security == 'advanced': 
            return set(request.access_token.oauth.mapped('rules.model.model')).issuperset(set(scopes))    
        if request.access_token.expires_in is not None and datetime.datetime.utcnow() > request.access_token.expires_in:
            return False
        return True
    
    def validate_refresh_token(self, refresh_token, client, request, *args, **kwargs):
        request.refresh_token = self.get_refresh_token(refresh_token)
        if request.refresh_token and consteq(request.refresh_token.oauth.client_id, client.client_id):
            request.user = request.refresh_token.user.id
            return True
        return False   
        
    #----------------------------------------------------------
    # Authenticate
    #----------------------------------------------------------

    def authenticate_client(self, request, *args, **kwargs):
        request = self.ensure_client_parameters(request)
        if not request.client:
            request.client = self.get_client(request.client_id)
        if not request.client:
            return False
        if request.client_secret is not None and request.client.client_secret != request.client_secret:
            return False
        return True

    def authenticate_client_id(self, client_id, request, *args, **kwargs):
        request = self.ensure_client_parameters(request)
        if not client_id:
            client_id = request.client_id
        if not request.client:
            request.client = self.get_client(client_id)
        return request.client and consteq(request.client.client_id, client_id)
    
    #----------------------------------------------------------
    # Confirm
    #----------------------------------------------------------
    
    def confirm_redirect_uri(self, client_id, code, redirect_uri, client, request, *args, **kwargs):
        if not request.client:
            request.client = self.get_client(client_id)
        authorization_code = self.get_authorization_code(code)
        return authorization_code.callback == redirect_uri
    
    #----------------------------------------------------------
    # Getter
    #----------------------------------------------------------

    def get_client(self, client_id):
        domain = [('client_id', '=', client_id)]
        client = http.request.env['muk_rest.oauth2'].sudo().search(domain, limit=1)
        return client.exists() and client
      
    def get_default_scopes(self, client_id, request, *args, **kwargs):
        if not request.client:
            request.client = self.get_client(client_id)
        if request.client and request.client.security == 'advanced': 
            return request.client.mapped('rules.model.model')
        return []
    
    def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
        if not request.client:
            request.client = self.get_client(client_id)
        return request.client.default_callback.url
    
    def get_original_scopes(self, refresh_token, request, *args, **kwargs):
        if not request.refresh_token:
            request.refresh_token = self.get_refresh_token(refresh_token)
        if request.refresh_token and  request.refresh_token.oauth.security == 'advanced': 
            return request.refresh_token.oauth.mapped('rules.model.model')
        return []
             
    def get_authorization_code(self, code):
        domain = [('code', '=', code)]
        authorization_code = http.request.env['muk_rest.authorization_code'].sudo().search(domain, limit=1)
        return authorization_code.exists() and authorization_code
    
    def get_bearer_token(self, token):
        domain = [('access_token', '=', token)]
        token = http.request.env['muk_rest.bearer_token'].sudo().search(domain, limit=1)
        return token.exists() and token
    
    def get_refresh_token(self, token):
        domain = [('refresh_token', '=', token)]
        token = http.request.env['muk_rest.bearer_token'].sudo().search(domain, limit=1)
        return token.exists() and token
    
    #----------------------------------------------------------
    # Setter
    #----------------------------------------------------------
    
    def save_authorization_code(self, client_id, code, request, *args, **kwargs):
        http.request.env['muk_rest.authorization_code'].sudo().create({
            'oauth': request.client.id,
            'code': code['code'],
            'state': code['state'],
            'user': request.user,
            'callback': request.redirect_uri})
    
    def save_bearer_token(self, token, request, *args, **kwargs):
        timedelta = datetime.timedelta(seconds=token['expires_in'])
        expires_in = datetime.datetime.utcnow() + timedelta
        http.request.env['muk_rest.bearer_token'].sudo().create({
            'user': request.user,
            'oauth': request.client.id,
            'access_token': token['access_token'],
            'refresh_token': token.get('refresh_token', None),
            'expires_in': expires_in}) 
    
    #----------------------------------------------------------
    # Revoke
    #----------------------------------------------------------
    
    def revoke_token(self, token, token_type_hint, request, *args, **kwargs):
        return self.get_bearer_token(token).unlink()
