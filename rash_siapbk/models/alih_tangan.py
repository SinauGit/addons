from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class AlihTangan(models.Model):
    _name = 'alih.tangan'
    _description = 'Alih Tangan Kasus'