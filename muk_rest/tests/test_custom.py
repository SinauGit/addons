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
from odoo.addons.muk_rest.tests.common import active_authentication, RestfulCase

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

CUSTOM_URL = '/api/custom'
CUSTOM_DOMAIN_URL = '/domain'
CUSTOM_ACTION_URL = '/action'
CUSTOM_CODE_URL = '/code'

class CustomTestCase(RestfulCase):
    
    def setUp(self):
        super(CustomTestCase, self).setUp()
        self.domain_endpoint = self.env['muk_rest.endpoint'].create({
            'name': 'Domain Test',
            'endpoint': CUSTOM_DOMAIN_URL,
            'model': self.ref('base.model_res_partner'),
            'method': 'GET',
            'state': 'domain'})
        action = self.env['ir.actions.server'].create({
            'name': 'Action Action',
            'model_id': self.ref('base.model_res_partner'),
            'code': "log('testing')",
            'activity_user_type': 'specific',
            'state': 'code'})
        self.action_endpoint = self.env['muk_rest.endpoint'].create({
            'name': 'Action Test',
            'endpoint': CUSTOM_ACTION_URL,
            'model': self.ref('base.model_res_partner'),
            'action': action.id,
            'method': 'POST',
            'state': 'action'})
        self.code_endpoint = self.env['muk_rest.endpoint'].create({
            'name': 'Code Test',
            'endpoint': CUSTOM_CODE_URL,
            'code': "result = 1",
            'model': self.ref('base.model_res_partner'),
            'method': 'POST',
            'state': 'code'})
    
    @unittest.skipIf(not active_authentication, "Skipped because no authentication is available!")
    def test_domain(self):
        client = self.authenticate()
        response = client.get(self.url_prepare(CUSTOM_URL + CUSTOM_DOMAIN_URL))
        self.assertTrue(response)
        self.assertTrue(response.json())
        
    @unittest.skipIf(not active_authentication, "Skipped because no authentication is available!")
    def test_domain_simple(self):
        client = self.authenticate()
        self.domain_endpoint.write({'domain': '[["id","=",1]]'})
        response = client.get(self.url_prepare(CUSTOM_URL + CUSTOM_DOMAIN_URL))
        self.assertTrue(response)
        self.assertTrue(response.json())
        
    @unittest.skipIf(not active_authentication, "Skipped because no authentication is available!")
    def test_domain_field(self):
        client = self.authenticate()
        self.domain_endpoint.write({'domain_fields': [(6, 0, [self.ref('base.field_res_partner__name')])]})
        response = client.get(self.url_prepare(CUSTOM_URL + CUSTOM_DOMAIN_URL))
        self.assertTrue(response)
        self.assertTrue(response.json())
        
    @unittest.skipIf(not active_authentication, "Skipped because no authentication is available!")
    def test_domain_context(self):
        client = self.authenticate()
        self.domain_endpoint.write({'domain': '[["id","=",active_id]]'})
        response = client.get(self.url_prepare(CUSTOM_URL + CUSTOM_DOMAIN_URL), data={'id': 1})
        self.assertTrue(response)
        self.assertTrue(response.json())
        
    @unittest.skipIf(not active_authentication, "Skipped because no authentication is available!")
    def test_domain_demo(self):
        client = self.authenticate("demo", "demo")
        response = client.get(self.url_prepare(CUSTOM_URL + CUSTOM_DOMAIN_URL))
        self.assertTrue(response)
        self.assertTrue(response.json())
        
    @unittest.skipIf(not active_authentication, "Skipped because no authentication is available!")
    def test_action(self):
        client = self.authenticate()
        response = client.get(self.url_prepare(CUSTOM_URL + CUSTOM_ACTION_URL))
        self.assertTrue(response)
        self.assertTrue(response.json())
        
    @unittest.skipIf(not active_authentication, "Skipped because no authentication is available!")
    def test_code(self):
        client = self.authenticate()
        response = client.get(self.url_prepare(CUSTOM_URL + CUSTOM_CODE_URL))
        self.assertTrue(response)
        self.assertTrue(response.json())