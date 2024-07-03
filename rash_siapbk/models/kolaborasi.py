from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class Kolaborasi(models.Model):
    _name = 'kolaborasi'
    _description = 'Kolaborasi'