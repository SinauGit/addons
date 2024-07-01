# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class PrestasiSiswa(models.Model):
    _name = 'prestasi.siswa'
    _description = 'Prestasi Siswa'
    name = fields.Many2one('res.partner', string='Nama', domain="[('student', '=', True)]")
    class_id = fields.Many2one('ruang.kelas', 'Kelas')
    tanggal = fields.Date('Tanggal')
    jenis_lomba = fields.Char('Jenis Lomba')
    hasil_lomba = fields.Char('Hasil Lomba')
    penyelenggara = fields.Char('Penyelenggara')
    tingkat = fields.Selection([
        ('kabupaten', 'Kabupaten'),
        ('Kota', 'Kota'),
        ('provinsi', 'Provinsi'),
        ('nasional', 'Nasional'),
        ('internasional', 'Internasional')
    ], string='Tingkat')
    jumlah_peserta = fields.Integer('Jumlah Peserta')
    keterangan = fields.Text('Keterangan')
    sertifikat = fields.Binary('Sertifikat', attachment=True)