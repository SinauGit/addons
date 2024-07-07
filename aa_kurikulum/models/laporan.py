from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import tempfile
import binascii
import pandas as pd
from xhtml2pdf import pisa
import io
# import locale
# locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8'

class laporan_yayasan(models.Model):
        _name = 'laporan.yayasan'
        
        siswa_id = fields.Many2one('res.partner', string='Nama', domain="[('student', '=', True)]")
        nisq = fields.Char('NISQ', related='siswa_id.nis')
        guru_id = fields.Many2one('hr.employee', string='Nama Halaqah')
        jumlah_santri = fields.Char('Jumlah Santri')
        total = fields.Char('Total')
        jenjang = fields.Selection('Jenjang', related='siswa_id.jenjang')
        jumlah = fields.Char('Jumlah')
        
        laporan_id = fields.Many2one('laporan.bulanan', string='Laporan Bulanan')
        
        
        # @api.constrains('siswa_id')
        # def _check_siswa_orangtua(self):
        #     for record in self:
        #         if record.siswa_id.orangtua_id !=  self.env.user.partner_id:
        #             raise models.ValidationError(_("Anda tidak dapat mencetak untuk keluarga orang lain."))
                
  
class laporan_bulanan(models.Model):
        _name = 'laporan.bulanan'
        
        
        name = fields.Char('Nomor', default='New', required=True, readonly=True)
        guru_id = fields.Many2one('hr.employee', string='Wali Kelas',related='class_id.guru_id')
        # guru_id = fields.Char('Wali kelas', related='class_id.guru_id')
        class_id = fields.Many2one('master.kelas', string='Group By', required=True)
        operator_id = fields.Many2one('hr.employee', string='Operator')
        
        komponen_line = fields.One2many('laporan.yayasan', 'laporan_id', string='Komponen')
        komponen_id = fields.Many2one('laporan.yayasan', string='komponen')
        nisq = fields.Char('NISQ', related='komponen_id.nisq')
        
        # tanggal_input = fields.Date('Tanggal Input') 
        tanggal_cetak = fields.Date('Tanggal Cetak', readonly=False, default=fields.Date.today)
        filename = fields.Char(string='Filename')
        data = fields.Binary(string='Data')
        
       
       
        def action_print_laporan(self):
            report = self.env.ref('aa_kurikulum.report_base_sekolah_laporan_bulanan').render(self.ids)
            pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            pisa.CreatePDF(io.BytesIO(report[0]), pdf_file)

            pdf_file.seek(0)
            pdf_data = pdf_file.read()
            pdf_file.close()
            judul = "Laporan Bulanan - {}".format(self.komponen_line.siswa_id.name)

            self.write({'data': binascii.b2a_base64(pdf_data),'filename': judul})

            return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/{}/data/{}?download=true'.format(self.id, judul),
            'target': 'self',
        }
        
        @api.model
        def create(self, vals):
                if vals.get('name', '/') == '/':
                        vals['name'] = self.env['ir.sequence'].next_by_code('laporan.bulanan') or '/'
                result = super(laporan_bulanan, self).create(vals)
                return result
            
        
        @api.multi
        def name_get(self):
            result = []
            for o in self:
                # name = 'Rekap Laporan Bulanan'
                name = "Rekap Laporan Bulanan - {}".format(o.name)
                result.append((o.id, name))
            return result
        
        
class RekapLaporanBulanan(models.Model):
    _name = 'rekap.laporan.bulanan'
    
    
    date = fields.Date('Tanggal Cetak')
    siswa_id = fields.Many2one('res.partner', string='Nama Santri', domain="[('student', '=', True)]")
    bulanan_id = fields.Many2one('laporan.bulanan', string='Laporan Bulanan')
    data = fields.Binary(string='Data')
    # attachment_ids = fields.Many2many(
    #     'ir.attachment', string="File Laporan Bulanan", copy=False)
    
    
    @api.multi
    def name_get(self):
        result = []
        for o in self:
            # name = 'Rekap Laporan Bulanan'
            name = "Rekap Laporan Bulanan - {}".format(o.siswa_id.name)
            result.append((o.id, name))
        return result
    
class RekapRapot(models.Model):
    _name = 'rekap.rapot'
    
    
    # siswa_id = fields.Many2one('res.partner', string='Siswa', domain="[('student', '=', True)]")
    guru_id = fields.Many2one('hr.employee', string='Nama Guru')
    # mapel = fields.Char(string='Mata Pelajaran', related='guru_id.job_id.name')
    mapel_id = fields.Many2one('mata.pelajaran',string='Mata Pelajaran')
    tgl_input = fields.Date('Tanggal Input', default=fields.Date.context_today)
    # mapel_id = fields.Many2one('hr.employee', string='Mata Pelajaran', related='guru_id.job_id')
    # class_id = fields.Many2one('ruang.kelas', string='Rombel', required=True)
    class_id = fields.Many2one('master.kelas', 'Rombel', domain="[('fiscalyear_id', '=', fiscalyear_id)]")
    
    kkm = fields.Integer('KKM')
    # rombel_id = fields.Many2one('ruang.kelas', string='Rombel')
    rapot_line = fields.One2many('rekap.rapot.line', 'rekap_id', 'Daftar Nilai' )
    fiscalyear_id = fields.Many2one('account.fiscalyear', string='Tahun Ajaran', required=True)
    total = fields.Integer('Total', compute="_compute_total")
    total_line = fields.Integer('Total Line', compute="_compute_total_line")
    rata = fields.Integer('Rata', compute="_compute_rata")
    date = fields.Date('Tanggal Cetak')
    
    
    @api.onchange('class_id')
    def _onchange_class_id(self):
        for rec in self:
            lines = [(5, 0, 0)]  
            for line in rec.class_id.res_line:
                val = {
                    'siswa_id': line.id,  
                }
                lines.append((0, 0, val)) 
            rec.rapot_line = lines 
    
    
    @api.multi
    def _compute_rata(self):
        for rec in self:
            if rec.total_line != 0:
                rec.rata = rec.total / rec.total_line
            else:
                rec.rata = 0  # Handle zero division case with an appropriate default value
    
    
    @api.depends('rapot_line')
    def _compute_total_line(self):
        for line in self:
            line.total_line = len(line.rapot_line)
                
    
    @api.depends('rapot_line')
    def _compute_total(self):
        for total in self:
            totals = 0
            for rec in self.rapot_line:
                totals += rec.nilai
            total.total = totals
            
            
            
    @api.constrains('guru_id', 'class_id')
    def _check_unique_siswa_id(self):
        for record in self:
            if record.guru_id and record.class_id:
                existing_records = self.env['rekap.rapot'].search([
                    ('guru_id', '=', record.guru_id.id),
                    ('class_id', '=', record.class_id.id),
                    ('id', '!=', record.id)  # Exclude current record
                ])
                if existing_records:
                    raise ValidationError('Mata Pelajaran dan kelas yang sama sudah ada.')
    
    @api.multi
    def name_get(self):
        result = []
        for o in self:
            name = "Rekap Rapot - {} - {}".format(o.mapel_id.name,  o.date)
            result.append((o.id, name))
        return result

    
    
    
class rekap_rapot_line(models.Model):
    _name = 'rekap.rapot.line'

    rekap_id = fields.Many2one('rekap.rapot', 'Buku Raport', required=True, ondelete='cascade')
    # siswa_id = fields.Many2one('res.partner', string='Nama', domain="[('student', '=', True)]")
    siswa_id = fields.Many2one('res.partner', 'Siswa', required=True, domain=[('student', '=', True)])
    name = fields.Many2one('mata.pelajaran', 'Mata Pelajaran')
    kkm = fields.Integer('KKM', related='rekap_id.kkm')
    # nilai = fields.Integer('Nilai')
    note = fields.Char('Catatan Guru')
    status = fields.Selection([
        ('remidi', 'REMIDI'),
        ('tuntas', 'TUNTAS')
    ], string='Status', compute='_compute_status', store=True)  
    
    nilai = fields.Integer('Nilai', compute='_compute_nilai', readonly=False)

    @api.depends('siswa_id')
    def _compute_nilai(self):
        for record in self:
            if record.siswa_id:
                # Cari field `avg` di model `score.line` berdasarkan `siswa_id`
                score_line = self.env['score.line'].search([('name', '=', record.siswa_id.id)], limit=1)
                record.nilai = score_line.avg if score_line else 0
            else:
                record.nilai = 0
    
    @api.depends('kkm', 'nilai')
    def _compute_status(self):
        for rec in self:
            if rec.kkm > rec.nilai:
                rec.status = 'remidi'
            else:
                rec.status = 'tuntas'
                
                
class Jadwal_Pelajaran(models.Model):
    _name = 'jadwal.pelajaran'
    
    pelajaran_id = fields.Many2one('mata.pelajaran', string='Mata Pelajaran')
    guru_id = fields.Many2one('hr.employee', string='Nama Halaqah')
    class_id = fields.Many2one('ruang.kelas', string='Rombel')
    
    
    @api.multi
    def name_get(self):
        result = []
        for o in self:
            name = 'Jadwal Pelajaran'
            name = "Jadwal Pelajaran - {}".format(o.mapel_id)
            result.append((o.id, name))
        return result
    
    
    
        
       