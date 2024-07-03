from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class KonselingKelompok(models.Model):
    _name = 'konseling.kelompok'
    _description = 'Konseling Kelompok'