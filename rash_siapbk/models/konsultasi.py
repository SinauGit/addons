from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class Konsultasi(models.Model):
    _name = 'konsultasi'
    _description = 'Konsultasi'