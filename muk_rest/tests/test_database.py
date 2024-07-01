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

import io
import os
import logging
import requests
import unittest

from odoo import _, tools
from odoo.tests import common

from odoo.addons.muk_rest import validators, tools
from odoo.addons.muk_rest.tests.common import RestfulCase
from odoo.addons.muk_rest.tests.common import DISABLE_DATABASE_TESTS
from odoo.addons.muk_rest.tests.common import MASTER_PASSWORD, LOGIN, PASSWORD

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class DatabaseTestCase(RestfulCase):
    
    def test_database_list(self):
        response = self.url_open(self.url_prepare('/api/database/list'))
        self.assertTrue(response)
    
    def test_database_size(self):
        databases = self.url_open(self.url_prepare('/api/database/list')).json()['databases']
        response = self.url_open(self.url_prepare('/api/database/size/%s' % databases[0]))
        self.assertTrue(response)

    @unittest.skipIf(True, "Skipped to avoid side effects on the server.")
    def test_database_create_clone_delete(self):
        response = self.url_open(
            self.url_prepare('/api/database/create'),
            data = {
                'master_password': MASTER_PASSWORD,
                'database_name': "muk_rest_create_db_test",
                'admin_login': LOGIN,
                'admin_password': PASSWORD
            }, timeout=300)
        self.assertTrue(response)
        databases = self.url_open(self.url_prepare('/api/database/list')).json()        
        self.assertTrue("muk_rest_create_db_test" in databases['databases'])
        self.assertTrue("muk_rest_create_db_test" not in databases['incompatible_databases'])
        response = self.url_open(
            self.url_prepare('/api/database/duplicate'),
            data = {
                'master_password': MASTER_PASSWORD,
                'database_old': "muk_rest_create_db_test",
                'database_new': "muk_rest_create_clone_test"
            }, timeout=300)
        self.assertTrue(response)
        databases = self.url_open(self.url_prepare('/api/database/list')).json()    
        self.assertTrue("muk_rest_create_clone_test" in databases['databases'])
        self.assertTrue("muk_rest_create_clone_test" not in databases['incompatible_databases'])
        response = self.url_open(
            self.url_prepare('/api/database/drop'),
            data = {
                'master_password': MASTER_PASSWORD,
                'database_name': "muk_rest_create_db_test"}, 
            timeout=120)
        self.assertTrue(response)
        databases = self.url_open(self.url_prepare('/api/database/list')).json()        
        self.assertTrue("muk_rest_create_db_test" not in databases['databases'])
        self.assertTrue("muk_rest_create_db_test" not in databases['incompatible_databases'])
        response = self.url_open(
            self.url_prepare('/api/database/drop'),
            data = {
                'master_password': MASTER_PASSWORD,
                'database_name': "muk_rest_create_clone_test"}, 
            timeout=120)
        self.assertTrue(response)
        databases = self.url_open(self.url_prepare('/api/database/list')).json()        
        self.assertTrue("muk_rest_create_clone_test" not in databases['databases'])
        self.assertTrue("muk_rest_create_clone_test" not in databases['incompatible_databases'])

    @unittest.skipIf(DISABLE_DATABASE_TESTS, "Skipped to avoid side effects on the server.")
    def test_backup_restore(self):
        response = self.url_open(
            self.url_prepare('/api/database/create'),
            data = {
                'master_password': MASTER_PASSWORD,
                'database_name': "muk_rest_backup_db_test",
                'admin_login': LOGIN,
                'admin_password': PASSWORD
            }, timeout=300)
        self.assertTrue(response)
        databases = self.url_open(self.url_prepare('/api/database/list')).json()        
        self.assertTrue("muk_rest_backup_db_test" in databases['databases'])
        self.assertTrue("muk_rest_backup_db_test" not in databases['incompatible_databases'])
        response = self.url_open(
            self.url_prepare('/api/database/backup'),
            data = {
                'master_password': MASTER_PASSWORD,
                'database_name': "muk_rest_backup_db_test",
            }, timeout=300)
        self.assertTrue(response)
        backup_file = io.BytesIO(response.content)
        self.assertTrue(backup_file)
        response = self.opener.post(
            self.url_prepare('/api/database/restore'),
            data = {
                'master_password': MASTER_PASSWORD,
                'database_name': "muk_rest_restore_db_test"
            },
            files = {
                'backup_file': (
                    "backup.zip",
                    backup_file,
                    'application/x-zip-compressed',
                    {'Expires': '0'}
                )
            }, timeout=300)
        self.assertTrue(response)
        databases = self.url_open(self.url_prepare('/api/database/list')).json()    
        self.assertTrue("muk_rest_restore_db_test" in databases['databases'])
        self.assertTrue("muk_rest_restore_db_test" not in databases['incompatible_databases'])
        response = self.url_open(
            self.url_prepare('/api/database/drop'),
            data = {
                'master_password': MASTER_PASSWORD,
                'database_name': "muk_rest_backup_db_test"}, 
            timeout=120)
        self.assertTrue(response)
        databases = self.url_open(self.url_prepare('/api/database/list')).json()        
        self.assertTrue("muk_rest_backup_db_test" not in databases['databases'])
        self.assertTrue("muk_rest_backup_db_test" not in databases['incompatible_databases'])
        response = self.url_open(
            self.url_prepare('/api/database/drop'),
            data = {
                'master_password': MASTER_PASSWORD,
                'database_name': "muk_rest_restore_db_test"}, 
            timeout=120)
        self.assertTrue(response)
        databases = self.url_open(self.url_prepare('/api/database/list')).json()        
        self.assertTrue("muk_rest_restore_db_test" not in databases['databases'])
        self.assertTrue("muk_rest_restore_db_test" not in databases['incompatible_databases'])