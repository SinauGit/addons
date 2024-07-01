from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class KonveerensiKasus(models.Model):
    _name = 'konverensi.kasus'
    _description = 'Konverensi Kasus'