from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class BimbinganKlasikal(models.Model):
    _name = 'bimbingan.klasikal'
    _description = 'Bimbingan Klasikal'