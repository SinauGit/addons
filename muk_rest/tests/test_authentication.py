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
import urllib
import logging
import requests
import unittest

import requests

from odoo import _, SUPERUSER_ID
from odoo.tests import common

from odoo.addons.muk_rest.tests.common import RestfulCase
from odoo.addons.muk_utils.tools.security import generate_token

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

try:
    import oauthlib
    import requests_oauthlib
except ImportError:
    _logger.warning("The Python library requests_oauthlib is not installed, OAuth tests wont work.")
    requests_oauthlib = None

class AuthenticationTestCase(RestfulCase):
    
    def setUp(self):
        super(AuthenticationTestCase, self).setUp()
        self.oauth1_oob_client_key = generate_token()
        self.oauth1_oob_client_secret = generate_token()
        self.oauth1_callback_client_key = generate_token()
        self.oauth1_callback_client_secret = generate_token()
        self.oauth2_web_client_key = generate_token()
        self.oauth2_web_client_secret = generate_token()
        self.oauth2_mobile_client_key = generate_token()
        self.oauth2_mobile_client_secret = generate_token()
        self.oauth2_legacy_client_key = generate_token()
        self.oauth2_legacy_client_secret = generate_token()
        self.oauth2_backend_client_key = generate_token()
        self.oauth2_backend_client_secret = generate_token()
        self.env['muk_rest.oauth1'].create({
            'name': 'OAuth1 Test OOB',
            'consumer_key': self.oauth1_oob_client_key,
            'consumer_secret': self.oauth1_oob_client_secret})
        self.env['muk_rest.oauth1'].create({
            'name': 'OAuth1 Test Callback',
            'consumer_key': self.oauth1_callback_client_key,
            'consumer_secret': self.oauth1_callback_client_secret,
            'callbacks': [(0, 0, {'url': self.callback_url})]})
        oauth_web = self.env['muk_rest.oauth2'].create({
            'name': 'OAuth2 Test - Web Application Flow',
            'client_id': self.oauth2_web_client_key,
            'client_secret': self.oauth2_web_client_secret,
            'state': 'authorization_code',
            'callbacks': [(0, 0, {'url': self.callback_url})]})
        oauth_mobile = self.env['muk_rest.oauth2'].create({
            'name': 'OAuth2 Test - Mobile Application Flow',
            'client_id': self.oauth2_mobile_client_key,
            'client_secret': self.oauth2_mobile_client_secret,
            'state': 'implicit',
            'callbacks': [(0, 0, {'url': self.callback_url})]})
        self.env['muk_rest.oauth2'].create({
            'name': 'OAuth2 Test - Legacy Application Flow',
            'client_id': self.oauth2_legacy_client_key,
            'client_secret': self.oauth2_legacy_client_secret,
            'state': 'password'})
        self.env['muk_rest.oauth2'].create({
            'name': 'OAuth2 Test - Backend Application Flow',
            'client_id': self.oauth2_backend_client_key,
            'client_secret': self.oauth2_backend_client_secret,
            'state': 'client_credentials',
            'user': SUPERUSER_ID})

    @unittest.skipIf(not requests_oauthlib, "Skipped because Requests-OAuthlib is not installed!")
    def test_oauth1_oob_authentication(self):
        oauth = requests_oauthlib.OAuth1Session(self.oauth1_oob_client_key, 
            client_secret=self.oauth1_oob_client_secret, callback_uri='oob')
        fetch_response = oauth.fetch_request_token(self.oauth1_request_token_url)
        resource_owner_key = fetch_response.get('oauth_token')
        resource_owner_secret = fetch_response.get('oauth_token_secret')
        self.assertTrue(resource_owner_key)
        self.assertTrue(resource_owner_secret)
        self.assertTrue(self.url_open(oauth.authorization_url(self.oauth1_authorization_url)))
        data = {'oauth_token': resource_owner_key, 'login': self.login, 'password': self.password}
        verifier = self.url_open(self.oauth1_authorization_url, data=data).json()['oauth_verifier']
        self.assertTrue(verifier)
        oauth = requests_oauthlib.OAuth1Session(self.oauth1_oob_client_key,
            client_secret=self.oauth1_oob_client_secret, resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret, verifier=verifier)
        oauth_tokens = oauth.fetch_access_token(self.oauth1_access_token_url)
        resource_owner_key = oauth_tokens.get('oauth_token')
        resource_owner_secret = oauth_tokens.get('oauth_token_secret')
        self.assertTrue(resource_owner_key)
        self.assertTrue(resource_owner_secret)
        oauth = requests_oauthlib.OAuth1Session(self.oauth1_oob_client_key, 
            client_secret=self.oauth1_oob_client_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret)
        self.assertTrue(oauth.get(self.test_authentication_url))
    
    @unittest.skipIf(not requests_oauthlib, "Skipped because Requests-OAuthlib is not installed!")
    def test_oauth1_callback_authentication(self):
        oauth = requests_oauthlib.OAuth1Session(self.oauth1_callback_client_key, 
            client_secret=self.oauth1_callback_client_secret, callback_uri=self.callback_url)
        fetch_response = oauth.fetch_request_token(self.oauth1_request_token_url)
        resource_owner_key = fetch_response.get('oauth_token')
        resource_owner_secret = fetch_response.get('oauth_token_secret')
        self.assertTrue(resource_owner_key)
        self.assertTrue(resource_owner_secret)
        self.assertTrue(self.url_open(oauth.authorization_url(self.oauth1_authorization_url)))
        data = {'oauth_token': resource_owner_key, 'login': self.login, 'password': self.password}
        authorization_url = self.url_prepare(self.oauth1_authorization_url)
        response = self.opener.post(authorization_url, data=data, timeout=10, allow_redirects=False)
        callback = urllib.parse.urlparse(response.headers['Location'])
        verifier = urllib.parse.parse_qs(callback.query)['oauth_verifier'][0]
        self.assertTrue(verifier)
        oauth = requests_oauthlib.OAuth1Session(self.oauth1_callback_client_key,
            client_secret=self.oauth1_callback_client_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier)
        oauth_tokens = oauth.fetch_access_token(self.oauth1_access_token_url)
        resource_owner_key = oauth_tokens.get('oauth_token')
        resource_owner_secret = oauth_tokens.get('oauth_token_secret')
        self.assertTrue(resource_owner_key)
        self.assertTrue(resource_owner_secret)
        oauth = requests_oauthlib.OAuth1Session(self.oauth1_callback_client_key, 
            client_secret=self.oauth1_callback_client_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret)
        self.assertTrue(oauth.get(self.test_authentication_url))

    @unittest.skipIf(not requests_oauthlib, "Skipped because Requests-OAuthlib is not installed!")
    def test_oauth2_web_authentication(self):
        oauth = requests_oauthlib.OAuth2Session(self.oauth2_web_client_key, redirect_uri=self.callback_url)
        authorization_url, state = oauth.authorization_url(self.oauth2_authorization_url)
        self.assertTrue(authorization_url and state)
        self.assertTrue(self.url_open(authorization_url))
        data = {
            'client_id': self.oauth2_web_client_key,
            'login': self.login,
            'password': self.password, 
            'response_type': 'code',
            'state': state,
            'redirect_uri': self.callback_url,
            'scopes': ['dummy']}
        authorization_url = self.url_prepare(self.oauth2_authorization_url)
        response = self.opener.post(authorization_url, data=data, timeout=10, allow_redirects=False)
        token = oauth.fetch_token(self.oauth2_access_token_url, authorization_response=response.headers['Location'])
        self.assertTrue(token)
        self.assertTrue(oauth.get(self.test_authentication_url))

    @unittest.skipIf(not requests_oauthlib, "Skipped because Requests-OAuthlib is not installed!")
    def test_oauth2_mobile_authentication(self):
        client = oauthlib.oauth2.MobileApplicationClient(client_id=self.oauth2_mobile_client_key)
        oauth = requests_oauthlib.OAuth2Session(client=client)
        authorization_url, state = oauth.authorization_url(self.oauth2_authorization_url)
        self.assertTrue(authorization_url and state)
        self.assertTrue(self.url_open(authorization_url))
        data = {
            'client_id': self.oauth2_mobile_client_key,
            'login': self.login,
            'password': self.password, 
            'response_type': 'token',
            'state': state,
            'redirect_uri': self.callback_url,
            'scopes': ['dummy']}
        authorization_url = self.url_prepare(self.oauth2_authorization_url)
        response = self.opener.post(authorization_url, data=data, timeout=10, allow_redirects=False)
        token = oauth.token_from_fragment(response.headers['Location'])
        self.assertTrue(token)
        self.assertTrue(oauth.get(self.test_authentication_url))

    @unittest.skipIf(not requests_oauthlib, "Skipped because Requests-OAuthlib is not installed!")
    def test_oauth2_legacy_authentication(self):
        client = oauthlib.oauth2.LegacyApplicationClient(client_id=self.oauth2_legacy_client_key)
        oauth = requests_oauthlib.OAuth2Session(client=client)
        token = oauth.fetch_token(token_url=self.oauth2_access_token_url,
            client_id=self.oauth2_legacy_client_key, 
            client_secret=self.oauth2_legacy_client_secret,
            username=self.login, password=self.password)
        self.assertTrue(token)
        self.assertTrue(oauth.get(self.test_authentication_url))

    @unittest.skipIf(not requests_oauthlib, "Skipped because Requests-OAuthlib is not installed!")
    def test_oauth2_backend_authentication(self):
        client = oauthlib.oauth2.BackendApplicationClient(client_id=self.oauth2_backend_client_key)
        oauth = requests_oauthlib.OAuth2Session(client=client)
        token = oauth.fetch_token(token_url=self.oauth2_access_token_url,
            client_id=self.oauth2_backend_client_key, 
            client_secret=self.oauth2_backend_client_secret,
            username=self.login, password=self.password)
        self.assertTrue(token)
        self.assertTrue(oauth.get(self.test_authentication_url))

    @unittest.skipIf(not requests_oauthlib, "Skipped because Requests-OAuthlib is not installed!")
    def test_oauth2_refresh(self):
        client = oauthlib.oauth2.LegacyApplicationClient(client_id=self.oauth2_legacy_client_key)
        oauth = requests_oauthlib.OAuth2Session(client=client)
        token = oauth.fetch_token(token_url=self.oauth2_access_token_url,
            client_id=self.oauth2_legacy_client_key, 
            client_secret=self.oauth2_legacy_client_secret,
            username=self.login, password=self.password)
        extra = {'client_id': self.oauth2_legacy_client_key, 'client_secret': self.oauth2_legacy_client_secret}
        refresh_token = oauth.refresh_token(token_url=self.oauth2_access_token_url, **extra)
        self.assertTrue(refresh_token)
        self.assertTrue(oauth.get(self.test_authentication_url))

    @unittest.skipIf(not requests_oauthlib, "Skipped because Requests-OAuthlib is not installed!")
    def test_oauth2_revoke(self):
        client = oauthlib.oauth2.LegacyApplicationClient(client_id=self.oauth2_legacy_client_key)
        oauth = requests_oauthlib.OAuth2Session(client=client)
        token = oauth.fetch_token(token_url=self.oauth2_access_token_url,
            client_id=self.oauth2_legacy_client_key, 
            client_secret=self.oauth2_legacy_client_secret,
            username=self.login, password=self.password)
        data = {'client_id': self.oauth2_legacy_client_key, 'token': token['access_token']}
        self.assertTrue(oauth.post(self.oauth2_revoke_url, data=data))
        self.assertFalse(oauth.get(self.test_authentication_url))
        