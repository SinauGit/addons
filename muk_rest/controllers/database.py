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
import ast
import json
import urllib
import logging
import tempfile
import datetime

from werkzeug import exceptions

from odoo import _, http, release, service
from odoo.http import request, Response
from odoo.exceptions import AccessDenied
from odoo.tools import misc, config
from odoo.sql_db import db_connect

from odoo.addons.muk_rest import validators, tools
from odoo.addons.muk_utils.tools.json import ResponseEncoder, RecordEncoder

_logger = logging.getLogger(__name__)

DBNAME_PATTERN = '^[a-zA-Z0-9][a-zA-Z0-9_.-]+$'

class DatabaseController(http.Controller):

    #----------------------------------------------------------
    # Common
    #----------------------------------------------------------
    
    @http.route('/api/change_master_password', auth="none", type='http', methods=['POST'], csrf=False)
    @tools.common.parse_exception
    def change_password(self, password_new, password_old="admin" , **kw):
        http.dispatch_rpc('db', 'change_admin_password', [password_old, password_new])
        return Response(json.dumps(True), content_type='application/json;charset=utf-8', status=200)

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    @http.route('/api/database/list', auth="none", type='http', methods=['GET'], csrf=False)
    @tools.common.parse_exception
    def database_list(self, **kw):
        databases = http.db_list()
        incompatible_databases = service.db.list_db_incompatible(databases)
        result = {'databases': databases, 'incompatible_databases': incompatible_databases}
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)
    
    @http.route([
        '/api/database/size',
        '/api/database/size/<string:database_name>',
    ], auth="none", type='http', methods=['GET'], csrf=False)
    @tools.common.parse_exception
    def database_size(self, database_name, **kw):
        databases = http.db_list()
        database_size = [False, False]
        if database_name in databases:
            template = config.get('db_template')
            templates_list = tuple(set(['postgres', template]))
            with db_connect("postgres").cursor() as cursor:
                cursor.execute("""
                    SELECT pg_database_size('{dbname}'),
                        pg_size_pretty(pg_database_size('{dbname}'));
                """.format(dbname=database_name))
                database_size = cursor.fetchone()
        result = {'name': database_name, 'size': database_size[0], 'text': database_size[1]}
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)

    @http.route('/api/database/create', auth="none", type='http', methods=['POST'], csrf=False)
    @tools.common.parse_exception
    def database_create(self, database_name, admin_login, admin_password, master_password="admin", lang="en_US", **kw):
        if not re.match(DBNAME_PATTERN, database_name):
            raise exceptions.BadRequest(_('Invalid database name.'))
        http.dispatch_rpc('db', 'create_database', [
            master_password, database_name,
            bool(kw.get('demo')), lang,
            admin_password, admin_login,
            kw.get('country_code') or False])
        return Response(json.dumps(True), content_type='application/json;charset=utf-8', status=200)
    
    @http.route('/api/database/duplicate', auth="none", type='http', methods=['POST'], csrf=False)
    @tools.common.parse_exception
    def database_duplicate(self, database_old, database_new, master_password="admin", **kw):
        if not re.match(DBNAME_PATTERN, database_new):
            raise exceptions.BadRequest(_('Invalid database name.'))
        http.dispatch_rpc('db', 'duplicate_database', [master_password, database_old, database_new])
        return Response(json.dumps(True), content_type='application/json;charset=utf-8', status=200)
    
    @http.route('/api/database/drop', auth="none", type='http', methods=['POST'], csrf=False)
    @tools.common.parse_exception
    def database_drop(self, database_name, master_password="admin", **kw):
        http.dispatch_rpc('db','drop', [master_password, database_name])
        request._cr = None
        return Response(json.dumps(True), content_type='application/json;charset=utf-8', status=200)

    #----------------------------------------------------------
    # Backup & Restore
    #----------------------------------------------------------        
    
    @http.route('/api/database/backup', auth="none", type='http', methods=['POST'], csrf=False)
    def database_backup(self, database_name, master_password="admin", backup_format='zip', **kw):
        service.db.check_super(master_password)
        ts = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        filename = "%s_%s.%s" % (database_name, ts, backup_format)
        headers = [
            ('Content-Type', 'application/octet-stream; charset=binary'),
            ('Content-Disposition', http.content_disposition(filename)),
        ]
        dump_stream = service.db.dump_db(database_name, None, backup_format)
        return Response(dump_stream, headers=headers, direct_passthrough=True)
            
    @http.route('/api/database/restore', auth="none", type='http', methods=['POST'], csrf=False)
    def restore(self, backup_file, database_name, master_password="admin", copy=False, **kw):
        service.db.check_super(master_password)
        try:
            with tempfile.NamedTemporaryFile(delete=False) as file:
                backup_file.save(file)
            service.db.restore_db(database_name, file.name, misc.str2bool(copy))
            return Response(json.dumps(True), content_type='application/json;charset=utf-8', status=200)
        except Exception:
            raise
        finally:
            os.unlink(file.name)