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
import logging
import requests

from odoo import _, http, tools, SUPERUSER_ID
from odoo.tests import common

from odoo.addons.muk_utils.tools.json import ResponseEncoder
from odoo.addons.muk_utils.tools.security import generate_token

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

try:
    import oauthlib
    import requests_oauthlib
except ImportError:
    _logger.warning("The Python library requests_oauthlib is not installed, OAuth authentication wont work.")
    requests_oauthlib = False
finally:
    active_authentication = bool(requests_oauthlib)
    
if os.environ.get('MUK_REST_ENABLE_DATABASE_TESTS'):
    DISABLE_DATABASE_TESTS = False
else:
    DISABLE_DATABASE_TESTS = True

HOST = '127.0.0.1'
PORT = tools.config['http_port']
MASTER_PASSWORD = tools.config['admin_passwd'] or "admin"

LOGIN = "admin"
PASSWORD = "admin"

CLIENT_KEY = "1234567890123456789012345"
CLIENT_SECRET = "1234567890123456789012345"
CALLBACK_URL = 'https://127.0.0.1/callback'

VERSION_URL = '/api'
DATABASE_URL = '/api/database'

OAUTH1_REQUEST_TOKEN_URL = '/api/authentication/oauth1/initiate'
OAUTH1_AUTHORIZATION_URL = '/api/authentication/oauth1/authorize'
OAUTH1_ACCESS_TOKEN_URL = '/api/authentication/oauth1/token'

OAUTH2_AUTHORIZATION_URL = '/api/authentication/oauth2/authorize'
OAUTH2_ACCESS_TOKEN_URL = '/api/authentication/oauth2/token'
OAUTH2_REVOKE_URL = '/api/authentication/oauth2/revoke'

TEST_AUTHENTICATION_URL = '/api/search/res.partner'

FIELD_NAMES_URL = '/api/field_names'
FIELDS_URL = '/api/fields'
METADATA_URL = '/api/metadata'

USER_URL = '/api/user'
USERINFO_URL = '/api/userinfo'
SESSION_URL = '/api/session'
CALL_URL = '/api/call'
XMLID_URL = '/api/xmlid'
BINARY_URL = '/api/binary'
UPLOAD_URL = '/api/upload'
REPORT_URL = '/api/report'
REPORTS_URL = '/api/reports'

SEARCH_URL = '/api/search'
NAME_URL = '/api/name'
READ_URL = '/api/read'
SEARCH_READ_URL = '/api/search_read'
READ_GROUP_URL = '/api/read_group'
CREATE_URL = '/api/create'
WRITE_URL = '/api/write'
UNLINK_URL = '/api/unlink'

ACCESS_URL = '/api/access'
ACCESS_RIGHTS_URL = '/api/access/rights'
ACCESS_RULES_URL = '/api/access/rules'
ACCESS_FIELDS_URL = '/api/access/fields'

class RestfulCase(common.HttpCase):
    
    def setUp(self):
        super(RestfulCase, self).setUp()
        self.login = LOGIN
        self.password = PASSWORD
        self.client_key = CLIENT_KEY
        self.client_secret = CLIENT_SECRET
        self.callback_url = CALLBACK_URL
        self.version_url = self.url_prepare(VERSION_URL)
        self.database_url = self.url_prepare(DATABASE_URL)
        self.oauth1_request_token_url = self.url_prepare(OAUTH1_REQUEST_TOKEN_URL)
        self.oauth1_authorization_url = self.url_prepare(OAUTH1_AUTHORIZATION_URL)
        self.oauth1_access_token_url = self.url_prepare(OAUTH1_ACCESS_TOKEN_URL)
        self.oauth2_authorization_url = self.url_prepare(OAUTH2_AUTHORIZATION_URL)
        self.oauth2_access_token_url = self.url_prepare(OAUTH2_ACCESS_TOKEN_URL)
        self.oauth2_revoke_url = self.url_prepare(OAUTH2_REVOKE_URL)
        self.test_authentication_url = self.url_prepare(TEST_AUTHENTICATION_URL)
        self.field_names_url = self.url_prepare(FIELD_NAMES_URL)
        self.fields_url = self.url_prepare(FIELDS_URL)
        self.metadata_url = self.url_prepare(METADATA_URL)
        self.user_url = self.url_prepare(USER_URL)
        self.userinfo_url = self.url_prepare(USERINFO_URL)
        self.session_url = self.url_prepare(SESSION_URL)
        self.call_url = self.url_prepare(CALL_URL)
        self.xmlid_url = self.url_prepare(XMLID_URL)
        self.binary_url = self.url_prepare(BINARY_URL)
        self.upload_url = self.url_prepare(UPLOAD_URL)
        self.report_url = self.url_prepare(REPORT_URL)
        self.reports_url = self.url_prepare(REPORTS_URL)
        self.search_url = self.url_prepare(SEARCH_URL)
        self.name_url = self.url_prepare(NAME_URL)
        self.read_url = self.url_prepare(READ_URL)
        self.search_read_url = self.url_prepare(SEARCH_READ_URL)
        self.read_group_url = self.url_prepare(READ_GROUP_URL)
        self.create_url = self.url_prepare(CREATE_URL)
        self.write_url = self.url_prepare(WRITE_URL)
        self.unlink_url = self.url_prepare(UNLINK_URL)
        self.access_url = self.url_prepare(ACCESS_URL)
        self.access_rights_url = self.url_prepare(ACCESS_RIGHTS_URL)
        self.access_rules_url = self.url_prepare(ACCESS_RULES_URL)
        self.access_fields_url = self.url_prepare(ACCESS_FIELDS_URL)
        self.test_client_key = generate_token()
        self.test_client_secret = generate_token()
        self.env['muk_rest.oauth2'].create({
            'name': 'OAuth2 Test',
            'client_id': self.test_client_key,
            'client_secret': self.test_client_secret,
            'state': 'password'})
        self.origin_transport = os.environ.get('OAUTHLIB_INSECURE_TRANSPORT')
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'OAUTHLIB_INSECURE_TRANSPORT'
                       
    def tearDown(self):
        super(RestfulCase, self).tearDown()
        if self.origin_transport:
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = self.origin_transport
        else:
            os.environ.pop('OAUTHLIB_INSECURE_TRANSPORT', None)
    
    def url_prepare(self, url):
        if url.startswith('/'):
            url = "http://%s:%s%s" % (HOST, PORT, url)
        return url
    
    def json_prepare(self, value, encoder=ResponseEncoder):
        return json.loads(json.dumps(value, sort_keys=True, indent=4, cls=encoder))
    
    def authenticate(self, login=LOGIN, password=PASSWORD):
        client = oauthlib.oauth2.LegacyApplicationClient(client_id=self.test_client_key)
        oauth = requests_oauthlib.OAuth2Session(client=client)
        token = oauth.fetch_token(token_url=self.oauth2_access_token_url,
            client_id=self.test_client_key, 
            client_secret=self.test_client_secret,
            username=login, password=password)
        return oauth