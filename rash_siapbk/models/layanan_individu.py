
from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class LayananIndividu(models.Model):
    _name = 'layanan.individu'
    _description = 'Layanan Individu'
    
    class_id = fields.Many2one('master.kelas', 'Kelas' )
    siswa_id = fields.Many2one('res.partner', string='Nama Siswa', domain="[('student', '=', True)]", required=True)
    nisn = fields.Char('NISN', related='siswa_id.nisn')
    # rombel = fields.Many2one('Rombel', related= 'siswa_id.rombel')
    konsolke = fields.Char('Konseling Ke')
    identifikasi = fields.Text('Identifikasi Masalah')
    pendekatan = fields.Selection([
        ('aldrean dan psikodinamik', 'aldrean dan psikodinamik'),
        ('belajar sosial', 'belajar sosial'),
        ('gestalt dan psikodrama', 'gestalt dan psikodrama'),
        ('humanistik dan fenomenologis', 'humanistik dan fenomenologis'),
        ('perilaku yang menggunakan hukuman', 'perilaku yang menggunakan hukuman'),
        ('perilaku kognitif', 'perilaku kognitif'),
        ('perilaku yang menggunakan reirfocement positif', 'perilaku yang menggunakan reirfocement positif'),
        ('solution - focused konseling', 'solution - focused konseling'),
        ('mindfulnes', 'mindfulnes'),
    ], string='Pendekatan')
    teknik = fields.Char('Teknik')
    komponen = fields.Selection([
         ('layanan dasar', 'layanan dasar'),
        ('layanan peminatan dan prencanaan individual', 'layanan peminatan dan prencanaan individual'),
        ('layanan responsif', 'layanan responsif'),
        ('dukungan sistem', 'dukungan sistem'),
    ], string='Komponen Layanan')
    bidang = fields.Selection([
        ('bimbingan pribadi', 'bimbingan pribadi'),
        ('bimbingan belajar', 'bimbingan belajar'),
        ('bimbingan sosial', 'bimbingan sosial'),
        ('bimbingan karir', 'bimbingan karir'),
    ], string='Bidang Bimbingan')
    jangka = fields.Text('Jangka Waktu Bimbingan')
    tempat = fields.Text('Tempat')
    penyebab = fields.Text('Penyebab Masalah')
    alternatif = fields.Text('Alternatif Pemecahan')
    hasil = fields.Text('Hasil')