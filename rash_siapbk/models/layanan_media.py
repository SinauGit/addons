from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class LayananMedia(models.Model):
    _name = 'layanan.media'
    _description = 'Layanan Media'