from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class BimbinganLintasKelas(models.Model):
    _name = 'bimbingan.lintas'
    _description = 'Bimbingan Lintas Kelas'