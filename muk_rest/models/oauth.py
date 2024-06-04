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
import datetime
import textwrap

from odoo import _, models, api, fields

_logger = logging.getLogger(__name__)

class OAuth(models.Model):
    
    _name = 'muk_rest.oauth'
    _description = "OAuth Configuration"
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------

    name = fields.Char(
        string="Name",
        required=True)
    
    active = fields.Boolean(
        string="Active",
        default=True)
    
    color = fields.Integer(
        string="Color")
    
    company = fields.Char(
        string="Company")
    
    homepage = fields.Char(
        string="Homepage URL")
    
    logo_url = fields.Char(
        string="Product logo URL")
    
    privacy_policy = fields.Char(
        string="Privacy policy URL")
    
    service_terms = fields.Char(
        string="Terms of service URL")
    
    description = fields.Text(
        string="Description")
    
    security = fields.Selection(
        selection=[
            ('basic', "Basic Access Control"),
            ('advanced', "Advanced Access Control")],
        string="Security",
        required=True,
        default='basic',
        help=textwrap.dedent("""\
            Defines the security settings to be used by the Restful API
            - Basic uses the user's security clearance to check requests from the API.
            - Advanced uses other rules in addition to the user security clearance, to further restrict the access.
            """))
    
    callbacks = fields.One2many(
        comodel_name='muk_rest.callback',
        inverse_name='oauth', 
        string="Callback URLs")
    
    rules = fields.One2many(
        comodel_name='muk_rest.access',
        inverse_name='oauth', 
        string="Access Rules")
    
    sessions = fields.Integer(
        compute='_compute_sessions',
        string="Sessions")
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.multi
    def action_settings(self):
        oauth_configuration_id = next(iter(self.ids or []), None)
        oauth1 = self.env['muk_rest.oauth1'].sudo().search([('oauth', '=', oauth_configuration_id)], limit=1)
        oauth2 = self.env['muk_rest.oauth2'].sudo().search([('oauth', '=', oauth_configuration_id)], limit=1)
        action = {
            'name': _("Settings"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
        }
        if oauth1.exists():
            action.update({
                'res_model': 'muk_rest.oauth1',
                'res_id': oauth1.id
            })
        elif oauth2.exists():
            action.update({
                'res_model': 'muk_rest.oauth2',
                'res_id': oauth2.id
            })
        return action
    
    @api.multi
    def action_sessions(self):
        oauth_configuration_id = next(iter(self.ids or []), None)
        oauth1 = self.env['muk_rest.oauth1'].sudo().search([('oauth', '=', oauth_configuration_id)], limit=1)
        oauth2 = self.env['muk_rest.oauth2'].sudo().search([('oauth', '=', oauth_configuration_id)], limit=1)
        action = {
            'name': _("Sessions"),
            'type': 'ir.actions.act_window',
            'views': [(False, 'tree'), (False, 'form')],
            'target': 'current',
        }
        if oauth1.exists():
            action.update({
                'res_model': 'muk_rest.access_token',
                'domain': [('oauth', '=', oauth1.id)],
            })
        elif oauth2.exists():
            action.update({
                'res_model': 'muk_rest.bearer_token',
                'domain': [('oauth', '=', oauth2.id)],
                'context': {'search_default_active': 1},
            })
        return action
    
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.multi
    def _compute_sessions(self):
        for record in self:
            domain_oauth1 = [('oauth.oauth', '=', record.id)]
            domain_oauth2 = [
                '&', ('oauth.oauth', '=', record.id), 
                '|', ('expires_in', '=', False), ('expires_in', '>', datetime.datetime.utcnow())]
            count_oauth1 = self.env['muk_rest.access_token'].sudo().search(domain_oauth1, count=True)
            count_oauth2 = self.env['muk_rest.bearer_token'].sudo().search(domain_oauth2, count=True)
            record.sessions = count_oauth1 + count_oauth2
