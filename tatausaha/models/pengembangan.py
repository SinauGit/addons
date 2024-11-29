from odoo import api, fields, models

class pengembangan_smp(models.Model):
    _name = 'pengembangan.smp'
    _description = 'Pengembangan Karir SMP'

    guru_id = fields.Many2one('hr.employee', string='Nama Guru')
    penyelenggara = fields.Char('Penyelenggara')
    waktu = fields.Datetime(string='Waktu')
    jenis = fields.Char(string='Jenis Kegiatan')
    tempat = fields.Char(string='Tempat')
    ket = fields.Char(string='Keterangan')

class pengembangan_sma(models.Model):
    _name = 'pengembangan.sma'
    _description = 'Pengembangan Karir SMA'

    guru_id = fields.Many2one('hr.employee', string='Nama Guru')
    penyelenggara = fields.Char('Penyelenggara')
    waktu = fields.Datetime(string='Waktu')
    jenis = fields.Char(string='Jenis Kegiatan')
    tempat = fields.Char(string='Tempat')
    ket = fields.Char(string='Keterangan')
    
class pengembangan_ustadz(models.Model):
    _name = 'pengembangan.ustadz'
    _description = 'Pengembangan Karir ustadz'

    name = fields.Char(string='Nama')
    penyelenggara = fields.Char('Penyelenggara')
    waktu = fields.Datetime(string='Waktu')
    jenis = fields.Char(string='Jenis Kegiatan')
    tempat = fields.Char(string='Tempat')
    ket = fields.Char(string='Keterangan')    