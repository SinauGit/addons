from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class KunjunganRumah(models.Model):
    _name = 'kunjungan.rumah'
    _description = 'Kunjungan Rumah'