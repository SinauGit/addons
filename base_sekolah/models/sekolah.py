import re
from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.osv.expression import get_unaccent_wrapper

import csv
import codecs
# import pandas as pd
import base64
from io import StringIO, BytesIO
# from openpyxl import Workbook
from openpyxl import load_workbook

jenjang = [
    ('TK', 'TK'), 
    ('SD1', 'SD - Kelas 1'), 
    ('SD2', 'SD - Kelas 2'), 
    ('SD3', 'SD - Kelas 3'), 
    ('SD4', 'SD - Kelas 4'), 
    ('SD5', 'SD - Kelas 5'), 
    ('SD6', 'SD - Kelas 6'), 
    ('SMP7', 'SMP - Kelas 7'), ('SMP8', 'SMP - Kelas 8'), ('SMP9', 'SMP - Kelas 9'), 
    ('SMA10', 'SMA - Kelas 10'), ('SMA11', 'SMA - Kelas 11'), ('SMA12', 'SMA - Kelas 12')
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


class master_kelas(models.Model):
    _name = 'master.kelas'
    _description = 'Master Kelas'
    res_line = fields.One2many('res.partner', 'class_id', string='siswa')
    name = fields.Char('Nama', required=True)
    lembaga = fields.Selection(lembaga, string='Lembaga', required=True, default='SD')
    grade = fields.Selection([
                            ('A', 'A'), ('B', 'B'),
                            ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'),
                            ('7', '7'), ('8', '8'), ('9', '9'),
                            ('10', '10'), ('11', '11'), ('12', '12')
                            ], string='Grade', required=True)
    rombel = fields.Selection([('banin', 'Banin'), ('banat', 'Banat')], string='Jenis', required=True, default='banin')
    guru_id = fields.Many2one('hr.employee', string='Wali Kelas')
    
    @api.multi
    def name_get(self):
        result = []
        for o in self:
            name = '[' + o.grade + '] ' + o.name
            result.append((o.id, name))
        return result


class mata_pelajaran(models.Model):
    _name = 'mata.pelajaran'
    _description = 'Mata Pelajaran'

    urut = fields.Integer('No. Urut', required=True)
    name = fields.Char('Nama', required=True)
    lembaga = fields.Selection(lembaga, string='Lembaga', required=True)
    

class ruang_kelas(models.Model):
    _name = 'ruang.kelas'
    _description = 'Ruang Kelas'

    name = fields.Many2one('master.kelas', 'Rombel', required=True)
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', required=True)
    lembaga = fields.Selection(lembaga, string='Lembaga', related='name.lembaga')
    siswa_ids = fields.Many2many('res.partner', 'siswa_rel', 'siswa_id', 'partner_id', 'Siswa', domain=[('student', '=', True)])
    res_line = fields.One2many('res.partner', 'class_id', string='siswa')
    data_file = fields.Binary('Import File')
    filename = fields.Char(string='Filename')

    _sql_constraints = [('name_uniq', 'unique(name, fiscalyear_id)', 'Kelas & Tahun Ajaran harus unik !')]

    @api.one
    def update_class(self):
        obj_invoice = self.env['account.invoice']

        iid = obj_invoice.search([('partner_id', 'in', [i.id for i in self.res_line])])
        if iid:
            iid.write({'class_id': self.name.name})

        for x in self.res_line:
            x.write({'class_id': self.name.name})
        return True
    
    
    # @api.multi
    # def import_siswa(self):
    #     if not self.data_file:
    #         raise UserError('Silahkan memilih file yang akan diimport!')

    #     # Membaca data file
    #     csv_data = base64.b64decode(self.data_file)
    #     data_file = StringIO(csv_data.decode("utf-8"))
        

    #     # Membaca file CSV
    #     csv_reader = csv.reader(data_file, delimiter=';')

    #     # Mengumpulkan data siswa dari file CSV
    #     siswa_data = []
    #     for row in csv_reader:
    #         nis, nisn, name = row  # Sesuaikan dengan kolom yang sesuai dengan data siswa
    #         siswa_data.append((0, 0, {'nis': nis, 'nisn': nisn, 'name': name}))

    #     # Memperbarui bidang siswa_ids dengan data siswa yang baru
    #     self.write({'siswa_ids': siswa_data})
            

    
    
    


    @api.multi
    def import_siswa(self):
        if not self.data_file:
            raise UserError(('Silahkan memilih file yang akan diimport !'))
        if self.siswa_ids:
            raise UserError(('Data siswa sudah terisi !'))

        csv_data = base64.b64decode(self.data_file)
        data_file = StringIO(csv_data.decode("utf-8"))
        data_file.seek(0)
        csv_reader = csv.reader(data_file, delimiter=';')

        res = []
        for row in csv_reader:
            res.append(int(row[0]))
            print (row)
            
        self.write({'siswa_ids': [(6, 0, res)]}) 
        
        
    
        



class hr_employee(models.Model):
    _inherit = 'hr.employee'

    nip = fields.Char('NIP')
    lembaga = fields.Selection(lembaga, string='Lembaga', default='SD')


class res_partner(models.Model):
    _inherit = 'res.partner'

    nis = fields.Char('NISQ')
    nisn = fields.Char('NISN')
    virtual_account = fields.Char('Virtual Account')
    pendaftaran_id = fields.Many2one('crm.lead', 'Pendaftaran', readonly=True)

    panggilan = fields.Char('Nama Panggilan')
    student = fields.Boolean('Siswa')
    parent = fields.Boolean('Orang Tua')
    guru = fields.Boolean('Guru')

    jenjang = fields.Selection(jenjang, string='Jenjang')
    class_id = fields.Many2one('master.kelas', 'Ruang Kelas')
    # ruang_id = fields.Many2one('ruang.kelas', 'Ruang Kelas')
    lembaga = fields.Selection(lembaga, string='Lembaga', related='class_id.lembaga', store=True)
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran')
    
    darah = fields.Selection([('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O'), ('-', '-')], 'Gol Darah', default='A')
    birth = fields.Date('Tanggal')
    place = fields.Char('Tempat')

    kelamin = fields.Selection([('Laki', 'Laki-Laki'), ('Perempuan', 'Perempuan')], 'Jenis Kelamin', default='Laki')
    agama = fields.Selection(religion, 'Agama', default='islam')
    warga = fields.Selection(negara, 'Kebangsaan', default='wni')

    anak_ke = fields.Integer('Anak Ke')
    kandung = fields.Integer('Kandung')
    tiri = fields.Integer('Tiri')
    angkat = fields.Integer('Angkat')

    bahasa = fields.Char('Bahasa di rumah', default='Indonesia')
    tinggal = fields.Char('Bertempat tinggal pada', default='Orang Tua')
    jarak = fields.Char('Jarak Sekolah (km)')
    berat = fields.Char('Berat Badan')
    tinggi = fields.Char('Tinggi Badan')
    moda = fields.Selection([('umum', 'Kendaraan Umum'), ('jalan', 'Jalan'), ('sepeda', 'Sepeda'), ('motor', 'Motor'), ('mobil', 'mobil')], 'Moda Transportasi')

    ayah = fields.Char('Nama')
    ibu = fields.Char('Nama')
    didika = fields.Selection(school, 'Pendidikan')
    didiki = fields.Selection(school, 'Pendidikan')
    kerja = fields.Char('Pekerjaan')
    kerji = fields.Char('Pekerjaan')
    hpa = fields.Char('No. HP')
    hpi = fields.Char('No. HP')
    agama_ayah = fields.Selection(religion, 'Agama', default='islam')
    warga_ayah = fields.Selection(negara, 'Kebangsaan', default='wni')
    warga_ibu = fields.Selection(negara, 'Kebangsaan', default='wni')
    gaji_ayah = fields.Selection(gaji, 'Penghasilan')
    gaji_ibu = fields.Selection(gaji, 'Penghasilan')

    # WALI
    wali_siswa = fields.Selection([('ayah', 'Ayah'), ('ibu', 'Ibu'), ('lain', 'Orang Lain')], 'Wali Siswa')
    wali = fields.Char('Nama')
    relasi = fields.Char('Hubungan')
    hpw = fields.Char('No. HP')
    agama_ibu = fields.Selection(religion, 'Agama', default='islam')
    didikw = fields.Selection(school, 'Pendidikan')
    pekerjaan = fields.Char('Pekerjaan')
    agama_wali = fields.Selection(religion, 'Agama', default='islam')
    warga_wali = fields.Selection(negara, 'Kebangsaan', default='wni')

    orangtua_id = fields.Many2one('res.partner', 'Orang Tua', compute='_compute_orangtua_id')
    anak_line = fields.One2many('res.partner', 'orangtua_id', 'Siswa')
    alamat = fields.Char('Alamat',compute='_compute_alamat_id')
    
    # ziyadah_line = fields.One2many('menu.ziyadah', 'siswa_id', string='Ziyadah')
    ziyadah_id = fields.Many2one('menu.ziyadah', string='Ziyadah')
    deresan_id = fields.Many2one('menu.deresan', string='Deresan')
    bk_id = fields.Many2one('bimbingan.konseling', string='Bimbingan Konseling Absen')
    bk_1_id = fields.Many2one('konseling.pelanggaran', string='Bimbingan Konseling Pelanggaran')
    bk_2_id = fields.Many2one('konseling.layanan', string='Bimbingan Konseling Layanan')
    rekap_id = fields.Many2one('rekap.rapot', string='Buku Raport')
    
    orang_user_id = fields.Many2one('res.users', string='Nama Orang Tua')

    # @api.constrains('orangtua_id')
    # def _check_parent_access(self):
    #     for record in self:
    #         orangtua_siswa = record.orangtua_id.parent_id
    #         orangtua_login = self.env.user.partner_id
    #         if orangtua_siswa != orangtua_login:
    #             raise models.ValidationError(_("Anda hanya bisa membuka form siswa anak Anda."))
    

    # sodara = fields.Boolean('Saudara')
    # sot = fields.Boolean('Anak Guru')
    # alumni = fields.Boolean('Alumni TK')
    # gelombang = fields.Selection([('g1', '1'), ('g2', '2'), ('g3', '3')], 'Gelombang')
    # jemput = fields.Selection([('pp', 'Pulang & Pergi'), ('pd', 'Pulang / Pergi'), ('la', 'Luar Area')], 'Antar Jemput')
    
    @api.depends('vat')
    def _compute_orangtua_id(self):
        for record in self:
            if record.vat:
                orangtua = self.env['res.partner'].search([('vat', '=', record.vat), ('parent', '=', True)], limit=1)
                if orangtua:
                    record.orangtua_id = orangtua.id
                else:
                    record.orangtua_id = False
                    
    @api.depends('tinggal')
    def _compute_alamat_id(self):
        for record in self:
            if record.tinggal:
                orangtua = self.env['res.partner'].search([('vat', '=', record.vat), ('student', '=', True)], limit=1)
                if orangtua:
                    record.alamat = orangtua.tinggal 
                else:
                    record.alamat = False

    @api.onchange('student')
    def onchange_student(self):
        if self.student:
            self.update({'student': self.student, 'customer': self.student, 'parent': not self.student})

    @api.onchange('parent')
    def onchange_parent(self):
        if self.parent:
            self.update({'student': not self.parent, 'customer': not self.parent, 'parent': self.parent})

    def _get_name(self):
        """ Utility method to allow name_get to be overrided without re-browse the partner """
        partner = self
        name = partner.name or ''
        if partner.nis:
            name = '[%s] %s' % (partner.nis or '-', partner.name)

        if partner.company_name or partner.parent_id:
            if not name and partner.type in ['invoice', 'delivery', 'other']:
                name = dict(self.fields_get(['type'])['type']['selection'])[partner.type]
            if not partner.is_company:
                name = "%s, %s" % (partner.commercial_company_name or partner.parent_id.name, name)
        if self._context.get('show_address_only'):
            name = partner._display_address(without_company=True)
        if self._context.get('show_address'):
            name = name + "\n" + partner._display_address(without_company=True)
        name = name.replace('\n\n', '\n')
        name = name.replace('\n\n', '\n')
        if self._context.get('address_inline'):
            name = name.replace('\n', ', ')
        if self._context.get('show_email') and partner.email:
            name = "%s <%s>" % (name, partner.email)
        if self._context.get('html_format'):
            name = name.replace('\n', '<br/>')
        if self._context.get('show_vat') and partner.vat:
            name = "%s ‒ %s" % (name, partner.vat)
        return name

  
            