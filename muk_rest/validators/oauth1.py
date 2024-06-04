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

import os
import re
import logging

from oauthlib.common import to_unicode
from oauthlib.oauth1 import SIGNATURE_HMAC, RequestValidator

from odoo import http, tools
from odoo.tools.misc import consteq

_logger = logging.getLogger(__name__)

class OAuth1RequestValidator(RequestValidator):
    
    #----------------------------------------------------------
    # Configuration
    #----------------------------------------------------------

    @property
    def client_key_length(self):
        return (20, 50)

    @property
    def request_token_length(self):
        return (20, 50)

    @property
    def access_token_length(self):
        return (20, 50)

    @property
    def nonce_length(self):
        return (20, 50)

    @property
    def verifier_length(self):
        return (20, 50)
    
    @property
    def enforce_ssl(self):
        if os.environ.get('OAUTHLIB_INSECURE_TRANSPORT'):
            return False
        return True
    
    #----------------------------------------------------------
    # Properties
    #----------------------------------------------------------

    @property
    def allowed_signature_methods(self):
        return (SIGNATURE_HMAC)

    @property
    def realms(self):
        return http.request.env['ir.model'].sudo().search([]).mapped('model')

    @property
    def dummy_client(self):
        return to_unicode('dummy_client', 'utf-8')

    @property
    def dummy_request_token(self):
        return to_unicode('dummy_request_token', 'utf-8')

    @property
    def dummy_access_token(self):
        return to_unicode('dummy_access_token', 'utf-8')

    #----------------------------------------------------------
    # Validate
    #----------------------------------------------------------
    
    def validate_client_key(self, client_key, request):
        if not request.client:
            request.client = self.get_client(client_key)
        return bool(request.client)

    def validate_request_token(self, client_key, token, request):
        if not request.request_token:
            request.request_token = self.get_request_token(token)
        return request.request_token and consteq(request.request_token.oauth.consumer_key, client_key)

    def validate_access_token(self, client_key, token, request):
        if not request.access_token:
            request.access_token = self.get_access_token(token)
        return request.access_token and consteq(request.access_token.oauth.consumer_key, client_key)
        
    def validate_timestamp_and_nonce(self, client_key, timestamp, nonce, request, request_token=None, access_token=None):
        domain = [
            ('client_key', '=', client_key),
            ('timestamp', '=', timestamp),
            ('nonce', '=', nonce),
            ('token', '=', request_token or access_token),
        ]
        model = http.request.env['muk_rest.request'].sudo()
        if model.search(domain).exists():
            return False
        model.create({
            'client_key': client_key,
            'timestamp': timestamp,
            'nonce': nonce,
            'token': request_token or access_token})
        return True

    def validate_redirect_uri(self, client_key, redirect_uri, request):
        if not request.client:
            request.client = self.get_client(client_key)
        if not request.client:
            return False
        if not request.client.callbacks.exists() and redirect_uri == 'oob':
            return True
        request.redirect_uri = redirect_uri
        return redirect_uri in request.client.callbacks.mapped('url')

    def validate_requested_realms(self, client_key, realms, request):
        if not request.client:
            request.client = self.get_client(client_key)
        if request.client and request.client.security == 'advanced': 
            return set(request.client.mapped('rules.model.model')).issuperset(set(realms))
        return True
        
    def validate_realms(self, client_key, token, request, uri=None, realms=None):
        if not request.request_token:
            request.request_token = self.get_request_token(token)
        if request.request_token and request.request_token.oauth.security == 'advanced': 
            return set(request_token.oauth.mapped('rules.model.model')).issuperset(set(realms))
        return True
        
    def validate_verifier(self, client_key, token, verifier, request):
        if not request.request_token:
            request.request_token = self.get_request_token(token)
        if (request.request_token and  consteq(request.request_token.verifier, verifier) and 
            consteq(request.request_token.oauth.consumer_key, client_key)):
            request.user = request.request_token.user.id
            return True
        return None

    def invalidate_request_token(self, client_key, request_token, request):
        if not request.request_token:
            request.request_token = self.get_request_token(token)
        if request.request_token and consteq(request.request_token.oauth.consumer_key, client_key):
            request.request_token.unlink()

    #----------------------------------------------------------
    # Getter
    #----------------------------------------------------------

    def get_client(self, client_key):
        domain = [('consumer_key', '=', client_key)]
        client = http.request.env['muk_rest.oauth1'].sudo().search(domain, limit=1)
        return client.exists() and client

    def get_client_secret(self, client_key, request):
        if not (request.client or request.client_secret):
            request.client = self.get_client(client_key)
        if request.client:
            request.client_secret = request.client.consumer_secret
        if request.client_secret:
            return request.client_secret
        return None

    def get_request_token(self, token):
        domain = [('resource_owner_key', '=', token)]
        token = http.request.env['muk_rest.request_token'].sudo().search(domain, limit=1)
        return token.exists() and token
    
    def get_request_token_secret(self, client_key, token, request):
        if not request.request_token:
            request.request_token = self.get_request_token(token)
        if request.request_token and consteq(request.request_token.oauth.consumer_key, client_key):
            return request.request_token.resource_owner_secret
        return None
    
    def get_access_token(self, token):
        domain = [('resource_owner_key', '=', token)]
        token = http.request.env['muk_rest.access_token'].sudo().search(domain, limit=1)
        return token.exists() and token
        
    def get_access_token_secret(self, client_key, token, request):
        if not request.access_token:
            request.access_token = self.get_access_token(token)
        if request.access_token and consteq(request.access_token.oauth.consumer_key, client_key):
            return request.access_token.resource_owner_secret
        return None
    
    def get_redirect_uri(self, token, request):
        if not request.request_token:
            request.request_token = self.get_request_token(token)
        if request.request_token and request.request_token.callback:
            return request.request_token.callback
        return 'oob'
    
    def get_default_realms(self, client_key, request):
        if not request.client:
            request.client = self.get_client(client_key)
        if request.client and request.client.security == 'advanced': 
            return request.client.mapped('rules.model.model')
        return []

    def get_realms(self, token, request):
        if not request.request_token:
            request.request_token = self.get_request_token(token)
        if request.request_token and request.request_token.oauth.security == 'advanced':
            return request.request_token.oauth.mapped('rules.model.model') 
        return []

    #----------------------------------------------------------
    # Setter
    #----------------------------------------------------------

    def save_request_token(self, token, request):
        http.request.env['muk_rest.request_token'].sudo().create({
            'oauth': request.client.id,
            'resource_owner_key': token['oauth_token'],
            'resource_owner_secret': token['oauth_token_secret'],
            'callback': request.redirect_uri})

    def save_verifier(self, token, verifier, request):
        domain = [('resource_owner_key', '=', token)]
        token = http.request.env['muk_rest.request_token'].sudo().search(domain)
        token.write({
            'verifier': verifier['oauth_verifier'],
            'user': verifier['user']
        })

    def save_access_token(self, token, request):
        http.request.env['muk_rest.access_token'].sudo().create({
            'user': request.user,
            'oauth': request.client.id,
            'resource_owner_key': token['oauth_token'],
            'resource_owner_secret': token['oauth_token_secret']})
    
    #----------------------------------------------------------
    # Verify
    #----------------------------------------------------------

    def verify_request_token(self, token, request):
        if not request.request_token:
            request.request_token = self.get_request_token(token)
        if request.request_token:
            return True
        return False

    def verify_realms(self, token, realms, request):
        if not request.request_token:
            request.request_token = self.get_request_token(token)
        if request.request_token and request.request_token.oauth.security == 'advanced': 
            return set(request.request_token.oauth.mapped('rules.model.model')).issuperset(set(realms))
        return True