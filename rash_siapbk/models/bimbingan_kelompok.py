from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class BimbinganKelompok(models.Model):
    _name = 'bimbingan.kelompok'
    _description = 'Bimbingan Kelompok'