from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

jenjang = [
    ('KB', 'KB'), 
    ('TKA', 'TK A'), 
    ('TKB', 'TK B'), 
    ('SD1', 'SD - Kelas 1'), 
    ('SD2', 'SD - Kelas 2'), 
    ('SD3', 'SD - Kelas 3'), 
    ('SD4', 'SD - Kelas 4'), 
    ('SD5', 'SD - Kelas 5'), 
    ('SD6', 'SD - Kelas 6'), 
    ('SMP7', 'SMP - Kelas 7'), 
    ('SMP8', 'SMP - Kelas 8'), 
    ('SMP9', 'SMP - Kelas 9'), 
    ('SMA10', 'SMA - Kelas 10'), 
    ('SMA11', 'SMA - Kelas 11'), 
    ('SMA12', 'SMA - Kelas 12')
]
school = [
    ('SD', 'SD'), ('SMP', 'SMP'), ('SMA', 'SMA'), 
    ('D1', 'D1'), ('D2', 'D2'), ('D3', 'D3'), ('D4', 'D4'), 
    ('S1', 'S1'), ('S2', 'S2'), ('S3', 'S3')
]
gaji = [
    ('0', 'Rp. 0 s/d Rp. 500.000'), 
    ('1', '> Rp. 500.000 s/d Rp. 1.000.000'), 
    ('2', '> Rp. 1.000.000 s/d Rp. 2.000.000'),
    ('3', '> Rp. 2.000.000 s/d Rp. 5.000.000'),
    ('4', '> Rp. 5.000.000'),
]
negara = [('wni', 'WNI'), ('wna', 'WNA'), ('turunan', 'WNI Keturunan')]
lembaga = [('KB', 'KB'), ('TK', 'TK'), ('SD', 'SD'), ('SMP', 'SMP'), ('SMA', 'SMA')]
religion = [('islam', 'Islam'), ('katolik', 'Katolik'), ('Protestan', 'Protestan'), ('hindu', 'Hindu'), ('budha', 'Budha')]


class Lead(models.Model):
    _inherit = "crm.lead"

    # nisn = fields.Char('NISN')
    # virtual_account = fields.Char('Virtual Account')
    # tipe = fields.Selection([('Manual', 'Manual'), ('Online', 'Online')], 'Cara Pendaftaran', default='Online', required=True)

    def _default_fiscalyear_id(self):
        today = fields.Date.today()
        return self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)], limit=1)
    
    user_id = fields.Many2one('res.users', string='User login', readonly=True, default=False)
    email_from = fields.Char('Email', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    nis = fields.Char('No. Pendaftaran', readonly=True)

    name = fields.Char('Opportunity', required=True, index=True, readonly=True, states={'Draft': [('readonly', False)]})
    panggilan = fields.Char('Nama Panggilan', readonly=True, states={'Draft': [('readonly', False)]})
    street = fields.Char('Street', readonly=True, states={'Draft': [('readonly', False)]})
    zip = fields.Char('Zip', readonly=True, states={'Draft': [('readonly', False)]})
    city = fields.Char('City', readonly=True, states={'Draft': [('readonly', False)]})
    country_id = fields.Many2one('res.country', string='Country', readonly=True, states={'Draft': [('readonly', False)]})
    phone = fields.Char('Phone', readonly=True, states={'Draft': [('readonly', False)]})
    mobile = fields.Char('Mobile', readonly=True, states={'Draft': [('readonly', False)]})

    jenjang = fields.Selection(jenjang, string='Jenjang', readonly=True, states={'Draft': [('readonly', False)]})
    lembaga = fields.Selection(lembaga, string='Lembaga', readonly=True, states={'Draft': [('readonly', False)]})
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', readonly=True, states={'Draft': [('readonly', False)]}, default=_default_fiscalyear_id)
    
    birth = fields.Date('Tanggal', readonly=True, states={'Draft': [('readonly', False)]})
    place = fields.Char('Tempat', readonly=True, states={'Draft': [('readonly', False)]})
    agama = fields.Selection(religion, 'Agama', default='islam', readonly=True, states={'Draft': [('readonly', False)]})
    warga = fields.Selection(negara, 'Kebangsaan', default='wni', readonly=True, states={'Draft': [('readonly', False)]})

    anak_ke = fields.Integer('Anak Ke', readonly=True, states={'Draft': [('readonly', False)]})
    kandung = fields.Integer('Kandung', readonly=True, states={'Draft': [('readonly', False)]})
    tiri = fields.Integer('Tiri', readonly=True, states={'Draft': [('readonly', False)]})
    angkat = fields.Integer('Angkat', readonly=True, states={'Draft': [('readonly', False)]})

    darah = fields.Selection([('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O'), ('-', '-')], 'Gol Darah', default='A', readonly=True, states={'Draft': [('readonly', False)]})
    kelamin = fields.Selection([('Laki', 'Laki-Laki'), ('Perempuan', 'Perempuan')], 'Jenis Kelamin', default='Laki', readonly=True, states={'Draft': [('readonly', False)]})
    bahasa = fields.Char('Bahasa di rumah', default='Indonesia', readonly=True, states={'Draft': [('readonly', False)]})
    tinggal = fields.Char('Tinggal Bersama', default='Orang Tua', readonly=True, states={'Draft': [('readonly', False)]})
    jarak = fields.Char('Jarak Sekolah (km)', readonly=True, states={'Draft': [('readonly', False)]})
    berat = fields.Char('Berat Badan', readonly=True, states={'Draft': [('readonly', False)]})
    tinggi = fields.Char('Tinggi Badan', readonly=True, states={'Draft': [('readonly', False)]})
    moda = fields.Selection([('umum', 'Kendaraan Umum'), ('jalan', 'Jalan'), ('sepeda', 'Sepeda'), ('motor', 'Motor'), ('mobil', 'Mobil')], 'Moda Transportasi', readonly=True, states={'Draft': [('readonly', False)]})

    ayah = fields.Char('Nama', readonly=True, states={'Draft': [('readonly', False)]})
    ibu = fields.Char('Nama', readonly=True, states={'Draft': [('readonly', False)]})
    didika = fields.Selection(school, 'Pendidikan', readonly=True, states={'Draft': [('readonly', False)]})
    didiki = fields.Selection(school, 'Pendidikan', readonly=True, states={'Draft': [('readonly', False)]})
    kerja = fields.Char('Pekerjaan', readonly=True, states={'Draft': [('readonly', False)]})
    kerji = fields.Char('Pekerjaan', readonly=True, states={'Draft': [('readonly', False)]})
    hpa = fields.Char('No. HP', readonly=True, states={'Draft': [('readonly', False)]})
    hpi = fields.Char('No. HP', readonly=True, states={'Draft': [('readonly', False)]})
    agama_ayah = fields.Selection(religion, 'Agama', default='islam', readonly=True, states={'Draft': [('readonly', False)]})
    agama_ibu = fields.Selection(religion, 'Agama', default='islam', readonly=True, states={'Draft': [('readonly', False)]})
    warga_ayah = fields.Selection(negara, 'Kebangsaan', default='wni', readonly=True, states={'Draft': [('readonly', False)]})
    warga_ibu = fields.Selection(negara, 'Kebangsaan', default='wni', readonly=True, states={'Draft': [('readonly', False)]})
    gaji_ayah = fields.Selection(gaji, 'Penghasilan', readonly=True, states={'Draft': [('readonly', False)]})
    gaji_ibu = fields.Selection(gaji, 'Penghasilan', readonly=True, states={'Draft': [('readonly', False)]})

    # WALI
    wali_siswa = fields.Selection([('ayah', 'Ayah'), ('ibu', 'Ibu'), ('lain', 'Wali')], 'Pengelola Akun', readonly=True, states={'Draft': [('readonly', False)]})
    wali = fields.Char('Nama', readonly=True, states={'Draft': [('readonly', False)]})
    relasi = fields.Char('Hubungan', readonly=True, states={'Draft': [('readonly', False)]})
    hpw = fields.Char('No. HP', readonly=True, states={'Draft': [('readonly', False)]})
    didikw = fields.Selection(school, 'Pendidikan', readonly=True, states={'Draft': [('readonly', False)]})
    pekerjaan = fields.Char('Pekerjaan', readonly=True, states={'Draft': [('readonly', False)]})
    agama_wali = fields.Selection(religion, 'Agama', default='islam', readonly=True, states={'Draft': [('readonly', False)]})
    warga_wali = fields.Selection(negara, 'Kebangsaan', default='wni', readonly=True, states={'Draft': [('readonly', False)]})

    # DOKUMEN
    akte_lahir = fields.Binary('Akte Kelahiran')
    kartu_keluarga = fields.Binary('Kartu Keluarga')
    ktp_ayah = fields.Binary('KTP Bapak')
    ktp_ibu = fields.Binary('KTP Ibu')
    ijazah_terakhir = fields.Binary('Ijazah Terakhir')
    foto_nisn = fields.Binary('Foto NISN')
    foto_siswa = fields.Binary('Pas Foto Calon Siswa')
    foto_keluarga = fields.Binary('Foto Keluarga Inti')
    sertifikat = fields.Binary('Sertifikat / Piagam')
    sertifikat2 = fields.Binary('Sertifikat / Piagam')
    sertifikat3 = fields.Binary('Sertifikat / Piagam')
    sertifikat4 = fields.Binary('Sertifikat / Piagam')
    sertifikat5 = fields.Binary('Sertifikat / Piagam')
    
    namafile_akte_lahir = fields.Char('Filename')
    namafile_kartu_keluarga = fields.Char('Filename')
    namafile_ktp_ayah = fields.Char('Filename')
    namafile_ktp_ibu = fields.Char('Filename')
    namafile_ijazah_terakhir = fields.Char('Filename')
    namafile_foto_nisn = fields.Char('Filename')
    namafile_foto_siswa = fields.Char('Filename')
    namafile_foto_keluarga = fields.Char('Filename')
    namafile_sertifikat = fields.Char('Filename')
    namafile_sertifikat2 = fields.Char('Filename')
    namafile_sertifikat3 = fields.Char('Filename')
    namafile_sertifikat4 = fields.Char('Filename')
    namafile_sertifikat5 = fields.Char('Filename')
    
    # CATATAN
    kekuatan = fields.Text('Menurut pengamatan Bapak dan Ibu, apakah kekuatan (strength) dan kelemahan (weakness) ananda ?', readonly=True, states={'Pernyataan': [('readonly', False)]})
    bakat = fields.Text('Menurut pengamatan Bapak dan Ibu, apakah ada bakat tertentu yang terlihat (menonjol) pada diri ananda ?', readonly=True, states={'Pernyataan': [('readonly', False)]})
    khusus = fields.Text('Apakah ada hal khusus terkait ananda yang ingin disampaikan ?', readonly=True, states={'Pernyataan': [('readonly', False)]})
    memilih = fields.Text('Megapa Bapak/Ibu memilih Sekolah Alam Citra Insani sebagai sekolah ananda ?', readonly=True, states={'Pernyataan': [('readonly', False)]})
    harapan = fields.Text('Apa harapan Bapak/Ibu terhadap Sekolah Alam Citra Insani ?', readonly=True, states={'Pernyataan': [('readonly', False)]})

    # PEMBAYARAN
    pembayaran1 = fields.Boolean('Pembayaran 1')
    pembayaran2 = fields.Boolean('Pembayaran 2')
    pembayaran3 = fields.Boolean('Pembayaran 3')

    # HASIL OBSERVASI
    namafile_hasil_observasi = fields.Char('Filename')
    hasil_observasi = fields.Binary('Hasil Observasi')
    
    state = fields.Selection([
        ('Draft', 'Input Profil'),
        ('Upload', 'Upload Dokumen'),
        ('Pernyataan', 'Pernyataan Orang Tua'),
        ('Ujian', 'Observasi'),
        ('Lulus', 'Lulus'),
        ('Tidak_Lulus', 'Tidak Lulus'),
        ('Bergabung', 'Bergabung'),
        ('Batal', 'Batal'),
        ('Undur_Diri', 'Mengundurkan Diri'),
    ], string='Status', readonly=True, copy=False, default='Draft', track_visibility='onchange')

    @api.model
    def create(self, vals):
        vals['nis'] = self.env['ir.sequence'].next_by_code('pendaftaran.siswa')
        user_id = self.create_login(vals)
        vals['user_id'] = user_id
        return super(Lead, self).create(vals) 
       
    @api.multi
    def create_login(self, vals):
        user = self.env['res.users'].create({
                            'name': vals['name'],
                            'login': vals['email_from'],
                            'password': 'saci',
                            'action_id': self.env.ref('aa_pendaftaran_online.pendaftaran_online_action').id,
                            'company_id': self.env.ref('base.main_company').id,
                            'groups_id': [(6, 0, [
                                self.env.ref('aa_pendaftaran_online.group_pendaftaran_calon_siswa').id,
                                self.env.ref('base.group_user').id
                            ])]
        })
        user.partner_id.email = vals['email_from']
        return user.id

    @api.multi
    def unlink(self):
        for o in self:
            if o.state != 'Draft':
                raise UserError(("Pendaftaran Siswa tidak bisa dihapus pada state %s !") % (o.state))
        return super(Lead, self).unlink()

    @api.multi
    def pendaftaran_lanjut(self):
        if self.state == 'Draft':
            self.write({'state': 'Upload'})
        elif self.state == 'Upload':
            self.write({'state': 'Pernyataan'})
        elif self.state == 'Pernyataan':
            self.write({'state': 'Ujian'})
        return True

    @api.multi
    def pendaftaran_balik(self):
        if self.state == 'Upload':
            self.write({'state': 'Draft'})
        elif self.state == 'Pernyataan':
            self.write({'state': 'Upload'})
        elif self.state == 'Ujian':
            self.write({'state': 'Pernyataan'})
        return True


    @api.multi
    def pendaftaran_draft(self):
        return self.write({'state': 'Draft'})

    @api.multi
    def pendaftaran_lulus(self):
        return self.write({'state': 'Lulus'})
    
    @api.multi
    def pendaftaran_tidak_lulus(self):
        self.pendaftaran_hapus()
        return self.write({'state': 'Tidak_Lulus'})
    
    @api.multi
    def pendaftaran_undur_diri(self):
        self.pendaftaran_hapus()
        return self.write({'state': 'Undur_Diri'})
    
    @api.multi
    def pendaftaran_hapus(self):
        self.user_id.unlink()
        self.user_id.partner_id.unlink()
        self.unlink()
        return True

    @api.multi
    def pendaftaran_gabung(self):
        nama_ortu = self.ayah 
        if self.wali_siswa == 'ibu' :
            nama_ortu = self.ibu
        elif self.wali_siswa == 'lain' :
            nama_ortu = self.wali
        
        ortu = self.env['res.partner'].create({
            'name': nama_ortu,
            'parent': True,
            'email': self.email_from,
            'street': self.street,
            'zip': self.zip,
            'city': self.city,
            'country_id': self.country_id.id,
            'phone': self.phone,
            'mobile': self.mobile,
            'user_id': self.user_id.id
        })

        self.user_id.partner_id.write({
            'name': self.name,
            'orangtua_id': ortu.id,
            'email': self.email_from,
            'street': self.street,
            'zip': self.zip,
            'city': self.city,
            'country_id': self.country_id.id,
            'phone': self.phone,
            'mobile': self.mobile,

            'nis': self.nis,
            'jenjang': self.jenjang,
            'lembaga': self.lembaga,
            'fiscalyear_id': self.fiscalyear_id.id,
            
            'birth': self.birth,
            'place': self.place,
            'agama': self.agama,
            'warga': self.warga,
            
            'anak_ke': self.anak_ke,
            'kandung': self.kandung,
            'tiri': self.tiri,
            'angkat': self.angkat,
            
            'panggilan': self.panggilan,
            'darah': self.darah,
            'kelamin': self.kelamin,
            'bahasa': self.bahasa,
            'tinggal': self.tinggal,
            'jarak': self.jarak,
            'berat': self.berat,
            'tinggi': self.tinggi,
            'moda': self.moda,

            'ayah': self.ayah,
            'ibu': self.ibu,
            'didika': self.didika,
            'didiki': self.didiki,
            'kerja': self.kerja,
            'kerji': self.kerji,
            'hpa': self.hpa,
            'hpi': self.hpi,
            'agama_ayah' : self.agama_ayah,
            'agama_ibu' : self.agama_ibu,
            'warga_ayah' : self.warga_ayah,
            'warga_ibu' : self.warga_ibu,
            'gaji_ayah' : self.gaji_ayah,
            'gaji_ibu' : self.gaji_ibu,

            'wali_siswa' : self.wali_siswa,
            'wali': self.wali,
            'hpw' : self.hpw,
            'agama_wali' : self.agama_wali,
            'warga_wali' : self.warga_wali,
            'relasi': self.relasi,
            'didikw': self.didikw,
            'pekerjaan': self.pekerjaan,
            
            'customer': True,
            'student': True,
        })
        return self.write({'state': 'Bergabung', 'partner_id': self.user_id.partner_id.id})

    @api.multi
    def cetak_kartu_ujian(self):
        return self.env.ref('aa_pendaftaran_online.report_pendaftaran_siswa_kartu_ujian').report_action(self)




# for o in self:
#     user = self.env['res.users'].create({
#                         'name': o.name,
#                         'login': o.email_from,
#                         'password': 'saci',
#                         'company_id': self.env.ref('base.main_company').id,
#                         'groups_id': [(6, 0, [
#                             self.env.ref('aa_pendaftaran_online.group_pendaftaran_calon_siswa').id,
#                             self.env.ref('base.group_user').id
#                         ])]
#                         })

#     o.write({'state': 'In_Progress', 'user_id': user.id})  
# return True

# access_registration_crm_team,crm.team,crm.model_crm_team,group_pendaftaran_calon_siswa,1,1,0,0
# access_registration_crm_lead_tag,crm.lead.tag,crm.model_crm_lead_tag,group_pendaftaran_calon_siswa,1,1,0,0
# access_registration_crm_stage,crm.stage,crm.model_crm_stage,group_pendaftaran_calon_siswa,1,1,0,0
# access_registration_crm_lost_reason,crm.lost.reason,crm.model_crm_lost_reason,group_pendaftaran_calon_siswa,1,1,0,0
# access_registration_res_partner,res.partner,base.model_res_partner,group_pendaftaran_calon_siswa,1,1,0,0
# access_registration_res_users,res.users,base.model_res_users,group_pendaftaran_calon_siswa,1,1,0,0
# access_registration_res_partner_category,res.partner.category.crm.manager,base.model_res_partner_category,group_pendaftaran_calon_siswa,1,0,0,0
# access_registration_crm_activity_report_user,crm.activity.report.user,crm.model_crm_activity_report,group_pendaftaran_calon_siswa,1,0,0,0
# access_registration_calendar_event_manager,calendar.event.manager,calendar.model_calendar_event,group_pendaftaran_calon_siswa,1,1,0,0
# access_registration_calendar_event_type_sale_manager,calendar.event.type.manager,calendar.model_calendar_event_type,group_pendaftaran_calon_siswa,1,1,0,0
# access_registration_mail_activity_type_sale_manager,mail.activity.type.sale.manager,mail.model_mail_activity_type,group_pendaftaran_calon_siswa,1,1,0,0
