import re
from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.osv.expression import get_unaccent_wrapper

class kamar(models.Model):
    _name = 'kamar'
    _description = 'Kamar'

    urut = fields.Integer('No. Urut', required=True)
    lembaga = fields.Selection(lembaga, string='Lembaga', default='SMP')
    grade = fields.Selection([
                            ('A', 'A'), ('B', 'B'),
                            ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'),
                            ('7', '7'), ('8', '8'), ('9', '9'),
                            ('10', '10'), ('11', '11'), ('12', '12')
                            ], string='Grade', required=True)
    siswa_id = fields.Many2one('master.kelas')