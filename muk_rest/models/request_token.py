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

import logging

from odoo import _, models, api, fields, SUPERUSER_ID

_logger = logging.getLogger(__name__)

class RequestToken(models.Model):
    
    _name = 'muk_rest.request_token'
    _description = "OAuth1 Request Token"

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------

    resource_owner_key = fields.Char(
        string="Token",
        required=True,
        readonly=True)
    
    resource_owner_secret = fields.Char(
        string="Token Secret",
        required=True,
        readonly=True)
    
    callback = fields.Char(
        string="Callback",
        readonly=True)
    
    verifier = fields.Char(
        string="Verifier",
        readonly=True)
    
    user = fields.Many2one(
        comodel_name='res.users',
        string="User",
        readonly=True,
        ondelete='cascade')
    
    oauth = fields.Many2one(
        comodel_name='muk_rest.oauth1',
        string="Configuration",
        required=True,
        readonly=True,
        ondelete='cascade')
    
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    def _read_from_database(self, field_names, inherited_field_names=[]):
        super(RequestToken, self)._read_from_database(field_names, inherited_field_names)
        protected_fields = ['resource_owner_key', 'resource_owner_secret', 'verifier']
        if self.env.uid != SUPERUSER_ID and set(protected_fields).intersection(field_names):
            for record in self:
                for field in protected_fields:
                    try:
                        record._cache[field]
                        record._cache[field] = '****************'
                    except:
                        pass