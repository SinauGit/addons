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

from odoo import _, models, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.muk_utils.tools import security

_logger = logging.getLogger(__name__)

class OAuth1(models.Model):
    
    _name = 'muk_rest.oauth1'
    _description = "OAuth1 Configuration"

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------

    oauth = fields.Many2one(
        comodel_name='muk_rest.oauth',
        string='OAuth',
        delegate=True,  
        required=True,
        ondelete='cascade')

    consumer_key = fields.Char(
        string="Consumer Key",
        required=True,
        default=lambda x: security.generate_token())
    
    consumer_secret = fields.Char(
        string="Consumer Secret",
        required=True,
        default=lambda x: security.generate_token())

    #----------------------------------------------------------
    # Constraints
    #----------------------------------------------------------
    
    _sql_constraints = [
        ('consumer_key_unique', 'UNIQUE (consumer_key)', 'Consumer Key must be unique.'),
        ('consumer_secret_unique', 'UNIQUE (consumer_secret)', 'Consumer Secret must be unique.'),
    ]
    
    @api.constrains('consumer_key')
    def check_consumer_key(self):
        for record in self:
            if not (20 < len(record.consumer_key) < 50):
                raise ValidationError(_("The consumer key must be between 20 and 50 characters long."))
            
    @api.constrains('consumer_secret')
    def check_consumer_secret(self):
        for record in self:
            if not (20 < len(record.consumer_secret) < 50):
                raise ValidationError(_("The consumer secret must be between 20 and 50 characters long."))
            
    #----------------------------------------------------------
    # Create / Update / Delete
    #----------------------------------------------------------

    @api.multi
    def unlink(self):
        self.mapped('oauth').unlink()
        return super(OAuth1, self).unlink()