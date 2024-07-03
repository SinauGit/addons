from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class KegiatanTambahan(models.Model):
    _name = 'kegiatan.tambahan'
    _description = 'Kegiatan Tambahan'