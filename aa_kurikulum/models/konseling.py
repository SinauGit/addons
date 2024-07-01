from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

# ABSEN
class BimbinganKonseling(models.Model):
    _name = 'bimbingan.konseling'
    
    name = fields.Char(string='No. Dokumen', default='/', required=True, readonly=True)
    guru_id = fields.Many2one('hr.employee', string='Nama Guru')
    siswa_id = fields.Many2one('res.partner', string='Nama Siswa', domain="[('student', '=', True)]", required=True)
    info = fields.Selection([
         ('sakit', 'Sakit'),
        ('ijin', 'Ijin'),
        ('alpa', 'Alpa'),
    ], string='Status')
    note = fields.Text('Catatan')
    count_sakit = fields.Char('Sakit')
    count_izin = fields.Char('Izin')
    count_alpa = fields.Char('Alpa')
    date = fields.Date('Date')
    date = fields.Datetime('Date')
    
    
    @api.model
    def create(self, vals):
        # Generate sequence if name is not provided
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('bimbingan.konseling') or '/'
        
        # Create the record
        record = super(BimbinganKonseling, self).create(vals)

        # Update the ziyadah_id in res.partner
        self._update_partner_bk_id(record.siswa_id.id, record.id)
        
        return record
    

    def write(self, vals):
        res = super(BimbinganKonseling, self).write(vals)
        for record in self:
            self._update_partner_bk_id(record.siswa_id.id, record.id)
        return res

    def _update_partner_bk_id(self, partner_id, bk_id):
        partner = self.env['res.partner'].browse(partner_id)
        if partner:
            partner.bk_id = bk_id
    
    # @api.constrains('siswa_id')
    # def _check_unique_siswa_id(self):
    #     for record in self:
    #         if record.siswa_id:
    #             existing_records = self.search([('siswa_id', '=', record.siswa_id.id)])
    #             if existing_records.exists() and len(existing_records) > 1:
    #                 existing_siswa_names = ', '.join(existing_records.mapped('siswa_id.name'))
    #                 raise ValidationError('Siswa {} sudah dipilih. Pilih siswa yang berbeda.'.format(existing_siswa_names))
    
    @api.multi
    def name_get(self):
        result = []
        for o in self:
            name = "Bimbingan Konseling - {}".format(o.siswa_id.name)
            # name = "Bimbingan Konseling"
            result.append((o.id, name))
        return result
    
    
# LAYANAN
class KonselingLayanan(models.Model):
    _name = 'konseling.layanan'
    
    
    guru_id = fields.Many2one('hr.employee', string='Nama Guru')
    niy = fields.Char('NIY')
    
    siswa_id = fields.Many2one('res.partner', string='Nama Santri', domain="[('student', '=', True)]", required=True)
    nisq = fields.Char('NISQ', related='siswa_id.nis')
    kelas = fields.Char('Kelas')
    tingkatan = fields.Selection('Tingkatan', related='siswa_id.jenjang')
    date = fields.Date('Date')
    # bulanan_id = fields.Many2one('laporan.bulanan', string='Laporan Bulanan')
    
    # Bimbingan Kel
    bimbingan_kel = fields.Selection([
        ('pribadi', 'Pribadi'),('belajar', 'Belajar'),('sosial', 'Sosial'),('karir', 'Karir'),
    ], string='Layanan')
    # pribadi_kel = fields.Char('Pribadi')
    # belajar_kel = fields.Char('Belajar')
    # sosial_kel = fields.Char('Sosial')
    # karir_kel = fields.Char('Karir')
    keterangan_kel = fields.Text('Keterangan')
    count_kel = fields.Char('Total Bimbingan Kel')
    
    # Bimbingan individu
    bimbingan_ind =  fields.Selection([
        ('pribadi', 'Pribadi'),('belajar', 'Belajar'),('sosial', 'Sosial'),('karir', 'Karir'),
    ], string='Layanan')
    # pribadi_ind = fields.Char('Pribadi')
    # belajar_ind = fields.Char('Belajar')
    # sosial_ind = fields.Char('Sosial')
    # karir_ind = fields.Char('Karir')
    keterangan_ind = fields.Text('Keterangan')
    count_ind = fields.Char('Total Bimbingan Individu')
    
    # konseling individu
    konseling =  fields.Selection([
        ('pribadi', 'Pribadi'),('belajar', 'Belajar'),('sosial', 'Sosial'),('karir', 'Karir'),
    ], string='Layanan')
    # pribadi_koind = fields.Char('Pribadi')
    # belajar_koind = fields.Char('Belajar')
    # sosial_koind = fields.Char('Sosial')
    # karir_koind = fields.Char('Karir')
    keterangan_koind = fields.Text('Keterangan')
    count_koind = fields.Char('Total Konseling Individu')
    
    # konsultasi
    konsultasi =  fields.Selection([
        ('pribadi', 'Pribadi'),('belajar', 'Belajar'),('sosial', 'Sosial'),('karir', 'Karir'),
    ], string='Layanan')
    # pribadi_kons = fields.Char('Pribadi')
    # belajar_kons = fields.Char('Belajar')
    # sosial_kons = fields.Char('Sosial')
    # karir_kons = fields.Char('Karir')
    keterangan_kons = fields.Text('Keterangan')
    count_kons = fields.Char('Total Konsultasi ')
    
    # mediasi
    mediasi =  fields.Selection([
        ('pribadi', 'Pribadi'),('belajar', 'Belajar'),('sosial', 'Sosial'),('karir', 'Karir'),
    ], string='Layanan')
    # pribadi_med = fields.Char('Pribadi')
    # belajar_med = fields.Char('Belajar')
    # sosial_med = fields.Char('Sosial')
    # karir_med = fields.Char('Karir')
    keterangan_med = fields.Text('Keterangan')
    count_med = fields.Char('Total Mediasi ')
    
    # ahli tangan kasus
    ahli =  fields.Selection([
        ('pribadi', 'Pribadi'),('belajar', 'Belajar'),('sosial', 'Sosial'),('karir', 'Karir'),
    ], string='Layanan')
    # pribadi_ahl = fields.Char('Pribadi')
    # belajar_ahl = fields.Char('Belajar')
    # sosial_ahl = fields.Char('Sosial')
    # karir_ahl = fields.Char('Karir')
    keterangan_ahl = fields.Text('Keterangan')
    count_ahl = fields.Char('Total Ahli Tangan Kasus ')
    
    # klasikal
    klasikal =  fields.Selection([
        ('pribadi', 'Pribadi'),('belajar', 'Belajar'),('sosial', 'Sosial'),('karir', 'Karir'),
    ], string='Layanan')
    # pribadi_klas = fields.Char('Pribadi')
    # belajar_klas = fields.Char('Belajar')
    # sosial_klas = fields.Char('Sosial')
    # karir_klas = fields.Char('Karir')
    keterangan_klas = fields.Text('Keterangan')
    count_klas = fields.Char('Total Klasikal ')
    
    @api.model
    def create(self, vals):
        record = super(KonselingLayanan, self).create(vals)
        self._update_partner_bk_2_id(record.siswa_id.id, record.id)
        return record

    def write(self, vals):
        res = super(KonselingLayanan, self).write(vals)
        for record in self:
            self._update_partner_bk_2_id(record.siswa_id.id, record.id)
        return res

    def _update_partner_bk_2_id(self, partner_id, bk_2_id):
        partner = self.env['res.partner'].browse(partner_id)
        if partner:
            partner.bk_2_id =  bk_2_id
    
   
    
    # @api.constrains('siswa_id')
    # def _check_unique_siswa_id(self):
    #     for record in self:
    #         if record.siswa_id:
    #             existing_records = self.search([('siswa_id', '=', record.siswa_id.id)])
    #             if existing_records.exists() and len(existing_records) > 1:
    #                 existing_siswa_names = ', '.join(existing_records.mapped('siswa_id.name'))
    #                 raise ValidationError('Siswa {} sudah dipilih. Pilih siswa yang berbeda.'.format(existing_siswa_names))
                
    @api.multi
    def name_get(self):
        result = []
        for o in self:
            name = "Konseling Layanan - {}".format(o.siswa_id.name)
            # name = "Konseling Layanan"
            result.append((o.id, name))
        return result
    
    
    
# PELANGGARAN
class KonselingPelaggaran(models.Model):
    _name = 'konseling.pelanggaran'
    
    nama = fields.Char(string='Nomor', default='/', required=True, readonly=True)
    siswa_id = fields.Many2one('res.partner', string='Nama Santri', domain="[('student', '=', True)]", required=True)
    info = fields.Selection([
        ('pelanggaran1', 'Pelanggaran Ringan'),
        ('pelanggaran2', 'Pelanggaran Berat'),
    ], string='Pelanggaran')
    waktu_pelanggaran = fields.Date('Waktu Pelanggaran')
    point = fields.Float('Point/Sanksi')
    keterangan = fields.Text('Keterangan')
    date = fields.Date('Date')
    
    @api.model
    def create(self, vals):
        # Generate sequence if name is not provided
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('konseling.pelanggaran') or '/'
        
        # Create the record
        record = super(KonselingPelaggaran, self).create(vals)

        # Update the ziyadah_id in res.partner
        self._update_partner_bk_1_id(record.siswa_id.id, record.id)
        
        return record
    

    def write(self, vals):
        res = super(KonselingPelaggaran, self).write(vals)
        for record in self:
            self._update_partner_bk_1_id(record.siswa_id.id, record.id)
        return res

    def _update_partner_bk_1_id(self, partner_id, bk_1_id):
        partner = self.env['res.partner'].browse(partner_id)
        if partner:
            partner.bk_1_id = bk_1_id
    
    # @api.constrains('siswa_id')
    # def _check_unique_siswa_id(self):
    #     for record in self:
    #         if record.siswa_id:
    #             existing_records = self.search([('siswa_id', '=', record.siswa_id.id)])
    #             if existing_records.exists() and len(existing_records) > 1:
    #                 existing_siswa_names = ', '.join(existing_records.mapped('siswa_id.name'))
    #                 raise ValidationError('Siswa {} sudah dipilih. Pilih siswa yang berbeda.'.format(existing_siswa_names))
    
    
    
    @api.multi
    def name_get(self):
        result = []
        for o in self:
            name = "Konseling Pelanggaran - {}".format(o.siswa_id.name)
            # name = "Konseling Pelanggaran "
            result.append((o.id, name))
        return result
    
 
    

   
    
    