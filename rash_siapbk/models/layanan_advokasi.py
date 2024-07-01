from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class LayananAdvokasi(models.Model):
    _name = 'layanan.advokasi'
    _description = 'Layanan Advokasi'