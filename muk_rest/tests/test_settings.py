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
import json
import urllib
import logging
import requests
import unittest

import requests

from odoo import _, SUPERUSER_ID
from odoo.tests import common

from odoo.addons.muk_rest import validators, tools
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

class SettingsTestCase(RestfulCase):
    
    def setUp(self):
        super(SettingsTestCase, self).setUp()
        self.oauth_settings_client_key = generate_token()
        self.oauth_settings_client_secret = generate_token()
        self.oatuh_settings_client = self.env['muk_rest.oauth2'].create({
            'name': "Settings Test",
            'client_id': self.oauth_settings_client_key,
            'client_secret': self.oauth_settings_client_secret,
            'state': 'password',
            'security': 'advanced',
            'rules': [(0, 0, {'model': self.ref('base.model_res_partner')})]})
        
    @unittest.skipIf(not requests_oauthlib, "Skipped because Requests-OAuthlib is not installed!")
    def test_oauth_valid(self):
        client = oauthlib.oauth2.LegacyApplicationClient(client_id=self.oauth_settings_client_key)
        oauth = requests_oauthlib.OAuth2Session(client=client)
        token = oauth.fetch_token(token_url=self.oauth2_access_token_url,
            client_id=self.oauth_settings_client_key, 
            client_secret=self.oauth_settings_client_secret,
            username=self.login, password=self.password)
        response = oauth.get(self.search_url, data={'model': 'res.partner'})
        self.assertTrue(response)
        
    @unittest.skipIf(not requests_oauthlib, "Skipped because Requests-OAuthlib is not installed!")
    def test_oauth_invalid(self):
        client = oauthlib.oauth2.LegacyApplicationClient(client_id=self.oauth_settings_client_key)
        oauth = requests_oauthlib.OAuth2Session(client=client)
        token = oauth.fetch_token(token_url=self.oauth2_access_token_url,
            client_id=self.oauth_settings_client_key, 
            client_secret=self.oauth_settings_client_secret,
            username=self.login, password=self.password)
        response = oauth.get(self.search_url, data={'model': 'res.users'})
        self.assertFalse(response)
        
    @unittest.skipIf(not requests_oauthlib, "Skipped because Requests-OAuthlib is not installed!")
    def test_oauth_operation(self):
        self.oatuh_settings_client.rules.write({'perm_read': False})
        client = oauthlib.oauth2.LegacyApplicationClient(client_id=self.oauth_settings_client_key)
        oauth = requests_oauthlib.OAuth2Session(client=client)
        token = oauth.fetch_token(token_url=self.oauth2_access_token_url,
            client_id=self.oauth_settings_client_key, 
            client_secret=self.oauth_settings_client_secret,
            username=self.login, password=self.password)
        response = oauth.get(self.search_url, data={'model': 'res.partner'})
        self.assertFalse(response)
        