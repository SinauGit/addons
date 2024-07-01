from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

nilai_adab = [
    ('1', '1 - Tumbuh'),
    ('2', '2 - Berkembang'),
    ('3', '3 - Pemantapan'),
    ('4', '4 - Melekat'),
]

BULAN = [
    ('Januari', 'Januari'), ('Februari', 'Februari'), ('Maret', 'Maret'),
    ('April', 'April'), ('Mei', 'Mei'), ('Juni', 'Juni'),
    ('Juli', 'Juli'), ('Agustus', 'Agustus'), ('September', 'September'),
    ('Oktober', 'Oktober'), ('November', 'November'), ('Desember', 'Desember')
]

class observasi_adab(models.Model):
    _name = 'observasi.adab'
    _description = 'Observasi Adab'
    _order = 'name desc'

    name = fields.Char(string='No. Dokumen', default='/', required=True, readonly=True)
    tanggal = fields.Date(string='Tanggal', required=True, states={'Done': [('readonly', True)]}, default=fields.Date.today)
    period_id = fields.Many2one('account.period', 'Period', domain=[('special', '=', False)], required=True, states={'Done': [('readonly', True)]})
    siswa_id = fields.Many2one('res.partner', 'Siswa', domain=[('student', '=', True)], required=True, states={'Done': [('readonly', True)]})
    kelas_id = fields.Many2one('master.kelas', 'Rombel', required=True, states={'Done': [('readonly', True)]})
    semester = fields.Selection([('Gasal', 'Gasal'), ('Genap', 'Genap')], string='Semester', required=True, states={'Done': [('readonly', True)]}, default='Gasal')
    urutan = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')], string='Observasi Ke-', required=True, states={'Done': [('readonly', True)]}, default='1')

    tauhid_1_1 = fields.Selection(nilai_adab, '1.1 - Tidak takut berlebihan kepada selain Allah', states={'Done': [('readonly', True)]})
    tauhid_1_2 = fields.Selection(nilai_adab, '1.2 - Mengesakan Allah dalam ucapan', states={'Done': [('readonly', True)]})
    tauhid_1_3 = fields.Selection(nilai_adab, '1.3 - Menunjukan kesyukuran dengan ucapan hamdalah', states={'Done': [('readonly', True)]})
    tauhid_1_4 = fields.Selection(nilai_adab, '1.4 - Membiasakan berwudhu dengan tertib dan benar', states={'Done': [('readonly', True)]})
    tauhid_1_5 = fields.Selection(nilai_adab, '1.5 - Membiasakan diri sholat fardhu dan tertib', states={'Done': [('readonly', True)]})
    tauhid_1_6 = fields.Selection(nilai_adab, '1.6 - Membiasakan diri berinfak', states={'Done': [('readonly', True)]})
    tauhid_1_7 = fields.Selection(nilai_adab, '1.7 - Membiasakan diri dzikrullah', states={'Done': [('readonly', True)]})
    tauhid_1_8 = fields.Selection(nilai_adab, '1.8 - Menghadiri majelis ilmu bersama orang tua', states={'Done': [('readonly', True)]})

    orangtua_2_1 = fields.Selection(nilai_adab, '2.1 - Mendengarkan dan mematuhi perintah/nasihat mereka', states={'Done': [('readonly', True)]})
    orangtua_2_2 = fields.Selection(nilai_adab, '2.2 - Memenuhi panggilan mereka', states={'Done': [('readonly', True)]})
    orangtua_2_3 = fields.Selection(nilai_adab, '2.3 - Merendah, kasih sayang dan tidak menyusahkan mereka', states={'Done': [('readonly', True)]})
    orangtua_2_4 = fields.Selection(nilai_adab, '2.4 - Berbuat baik dan sabar kepada mereka', states={'Done': [('readonly', True)]})
    orangtua_2_5 = fields.Selection(nilai_adab, '2.5 - Tidak curiga dan tidak membangkang mereka', states={'Done': [('readonly', True)]})

    disiplin_3_1 = fields.Selection(nilai_adab, '3.1 - Tidak terlambat dan tidak bolos sekolah', states={'Done': [('readonly', True)]})
    disiplin_3_2 = fields.Selection(nilai_adab, '3.2 - Menggunakan seragam sekolah secara tertib dan rapi', states={'Done': [('readonly', True)]})
    disiplin_3_3 = fields.Selection(nilai_adab, '3.3 - Merapikan hak milik pribadi dan menjaga hak milik orang lain', states={'Done': [('readonly', True)]})
    disiplin_3_4 = fields.Selection(nilai_adab, '3.4 - Menjaga dan merawat sarana umum dan perlengkapan sekolah', states={'Done': [('readonly', True)]})
    disiplin_3_5 = fields.Selection(nilai_adab, '3.5 - Bersikap jujur dan bertanggung jawab', states={'Done': [('readonly', True)]})
    disiplin_3_6 = fields.Selection(nilai_adab, '3.6 - Menolong teman dan saling menghargai', states={'Done': [('readonly', True)]})
    disiplin_3_7 = fields.Selection(nilai_adab, '3.7 - Berani minta maaf bila salah dan memaafkan kesalahan orang', states={'Done': [('readonly', True)]})

    pemimpin_4_1 = fields.Selection(nilai_adab, '4.1 - Menunjukan inisiatif & Pengaruh yang baik', states={'Done': [('readonly', True)]})
    pemimpin_4_2 = fields.Selection(nilai_adab, '4.2 - Mampu menyatakan pendapat', states={'Done': [('readonly', True)]})
    pemimpin_4_3 = fields.Selection(nilai_adab, '4.3 - Mampu menerima pendapat orang lain', states={'Done': [('readonly', True)]})
    pemimpin_4_4 = fields.Selection(nilai_adab, '4.4 - Menunjukan keteladanan pada kelompok', states={'Done': [('readonly', True)]})
    pemimpin_4_5 = fields.Selection(nilai_adab, '4.5 - Memberi tanggapan baik terhadap instruksi', states={'Done': [('readonly', True)]})
    pemimpin_4_6 = fields.Selection(nilai_adab, '4.6 - Mampu berbagi dalam kelompok', states={'Done': [('readonly', True)]})
    pemimpin_4_7 = fields.Selection(nilai_adab, '4.7 - Menunjukan kerja sama dalam dinamika kelompok', states={'Done': [('readonly', True)]})

    bersih_5_1 = fields.Selection(nilai_adab, '5.1 - Mengkonsumsi makanan yang halal dan sehat', states={'Done': [('readonly', True)]})
    bersih_5_2 = fields.Selection(nilai_adab, '5.2 - Meletakan sesuatu sesuai tempatnya', states={'Done': [('readonly', True)]})
    bersih_5_3 = fields.Selection(nilai_adab, '5.3 - Membuang sampah pada tempatnya', states={'Done': [('readonly', True)]})
    bersih_5_4 = fields.Selection(nilai_adab, '5.4 - Menjaga kebersihan dan kerapian pakaian', states={'Done': [('readonly', True)]})
    bersih_5_5 = fields.Selection(nilai_adab, '5.5 - Membiasakan berhemat dan tidak mubazir', states={'Done': [('readonly', True)]})
    bersih_5_6 = fields.Selection(nilai_adab, '5.6 - Membiasakan cuci tangan', states={'Done': [('readonly', True)]})
    bersih_5_7 = fields.Selection(nilai_adab, '5.7 - Membiasakan memotong kuku dan membersihkan telinga', states={'Done': [('readonly', True)]})
    bersih_5_8 = fields.Selection(nilai_adab, '5.8 - Rajin melaksanakan piket kebersihan kelas', states={'Done': [('readonly', True)]})
    bersih_5_9 = fields.Selection(nilai_adab, '5.9 - Menjaga kebersihan WC dan tempat wudhu', states={'Done': [('readonly', True)]})
    bersih_5_10 = fields.Selection(nilai_adab, '5.10 - Tertib dan benar dalam beristinja', states={'Done': [('readonly', True)]})
    bersih_5_11 = fields.Selection(nilai_adab, '5.11 - Membiasakan diri gosok gigi', states={'Done': [('readonly', True)]})

    mandiri_6_1 = fields.Selection(nilai_adab, '6.1 - Tidak ditunggu ortu/wali di rumah', states={'Done': [('readonly', True)]})
    mandiri_6_2 = fields.Selection(nilai_adab, '6.2 - Mampu makan dan minum sendiri', states={'Done': [('readonly', True)]})
    mandiri_6_3 = fields.Selection(nilai_adab, '6.3 - Berani ke kamar mandi sendiri', states={'Done': [('readonly', True)]})
    mandiri_6_4 = fields.Selection(nilai_adab, '6.4 - Mampu menggunakan dan merapikan peralatan pribadi', states={'Done': [('readonly', True)]})
    mandiri_6_5 = fields.Selection(nilai_adab, '6.5 - Menyelesaikan tugas sesuai kemampuan', states={'Done': [('readonly', True)]})
    mandiri_6_6 = fields.Selection(nilai_adab, '6.6 - Mampu mengendalikan sikap di saat-saat yang tidak nyaman', states={'Done': [('readonly', True)]})

    catt_tauhid_1_1 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_tauhid_1_2 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_tauhid_1_3 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_tauhid_1_4 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_tauhid_1_5 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_tauhid_1_6 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_tauhid_1_7 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_tauhid_1_8 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})

    catt_orangtua_2_1 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_orangtua_2_2 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_orangtua_2_3 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_orangtua_2_4 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_orangtua_2_5 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})

    catt_disiplin_3_1 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_disiplin_3_2 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_disiplin_3_3 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_disiplin_3_4 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_disiplin_3_5 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_disiplin_3_6 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_disiplin_3_7 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})

    catt_pemimpin_4_1 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_pemimpin_4_2 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_pemimpin_4_3 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_pemimpin_4_4 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_pemimpin_4_5 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_pemimpin_4_6 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_pemimpin_4_7 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})

    catt_bersih_5_1 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_bersih_5_2 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_bersih_5_3 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_bersih_5_4 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_bersih_5_5 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_bersih_5_6 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_bersih_5_7 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_bersih_5_8 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_bersih_5_9 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_bersih_5_10 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_bersih_5_11 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})

    catt_mandiri_6_1 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_mandiri_6_2 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_mandiri_6_3 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_mandiri_6_4 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_mandiri_6_5 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})
    catt_mandiri_6_6 = fields.Char('# Catatan', default='-', states={'Done': [('readonly', True)]})

    nilai_tauhid = fields.Integer(string='Subtotal', compute='_nilai_total', store=True)
    nilai_orangtua = fields.Integer(string='Subtotal', compute='_nilai_total', store=True)
    nilai_disiplin = fields.Integer(string='Subtotal', compute='_nilai_total', store=True)
    nilai_pemimpin = fields.Integer(string='Subtotal', compute='_nilai_total', store=True)
    nilai_bersih = fields.Integer(string='Subtotal', compute='_nilai_total', store=True)
    nilai_mandiri = fields.Integer(string='Subtotal', compute='_nilai_total', store=True)

    total_nilai = fields.Integer(string='Nilai Total', compute='_nilai_total', store=True)
    total_avg = fields.Float(string='Nilai Rata-Rata', compute='_nilai_rata', store=True)

    state = fields.Selection([
        ('Draft', 'Draft'),
        ('Approved_PIC', 'Input by Guru'),
        ('Approved_Wali', 'Input by Ortu/Wali'),
        ('Done', 'Done'),
    ], string='Status', readonly=True, copy=False, default='Draft')


    @api.onchange('kelas_id', 'siswa_id')
    def onchange_siswa(self):
        if self.siswa_id:
            self.update({'kelas_id': self.siswa_id.class_id.id})
        else:
            self.update({'kelas_id': False})

    @api.multi
    def observasi_open_pic(self):
        if not all([self.tauhid_1_2, self.tauhid_1_4, self.tauhid_1_6, self.tauhid_1_4,
        self.disiplin_3_1, self.disiplin_3_2, self.disiplin_3_3, self.disiplin_3_4, self.disiplin_3_5, self.disiplin_3_6, self.disiplin_3_7,
        self.pemimpin_4_1, self.pemimpin_4_2, self.pemimpin_4_3, self.pemimpin_4_4, self.pemimpin_4_5, self.pemimpin_4_6, self.pemimpin_4_7,
        self.bersih_5_3, self.bersih_5_8, self.bersih_5_9,
        self.mandiri_6_1, self.mandiri_6_2, self.mandiri_6_5]):
            raise UserError(("Harap mengisi semua pertanyaan !"))

        return self.write({'state': 'Approved_PIC', 'tanggal_approve_pic': datetime.today()})

    @api.multi
    def observasi_open_ortu(self):
        if not all([self.tauhid_1_1, self.tauhid_1_3, self.tauhid_1_5, self.tauhid_1_7, self.tauhid_1_8,
        self.orangtua_2_1, self.orangtua_2_2, self.orangtua_2_3, self.orangtua_2_4, self.orangtua_2_5,
        self.bersih_5_1, self.bersih_5_2, self.bersih_5_4, self.bersih_5_5, self.bersih_5_6, self.bersih_5_7, self.bersih_5_10, self.bersih_5_11,
        self.mandiri_6_3, self.mandiri_6_4, self.mandiri_6_6]):
            raise UserError(("Harap mengisi semua pertanyaan !"))

        return self.write({'state': 'Approved_Wali', 'tanggal_approve_ortu': datetime.today()})

    @api.multi
    def observasi_draft(self):
        return self.write({'state': 'Draft', 'tanggal_approve_pic': False, 'tanggal_approve_ortu': False})

    @api.multi
    def observasi_done(self):
        return self.write({'state': 'Done'})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('observasi.adab')
        return super(observasi_adab, self).create(vals)

    # @api.multi
    # def unlink(self):
    #     for o in self:
    #         if o.state != 'Draft':
    #             raise UserError(("Observasi adab tidak bisa dihapus pada state %s !") % (o.state))
    #     return super(observasi_adab, self).unlink()


    @api.depends('tauhid_1_1', 'tauhid_1_2', 'tauhid_1_3', 'tauhid_1_4', 'tauhid_1_5', 'tauhid_1_6', 'tauhid_1_7', 'tauhid_1_8',
    'orangtua_2_1', 'orangtua_2_2', 'orangtua_2_3', 'orangtua_2_4', 'orangtua_2_5',
    'disiplin_3_1', 'disiplin_3_2', 'disiplin_3_3', 'disiplin_3_4', 'disiplin_3_5', 'disiplin_3_6', 'disiplin_3_7',
    'pemimpin_4_1', 'pemimpin_4_2', 'pemimpin_4_3', 'pemimpin_4_4', 'pemimpin_4_5', 'pemimpin_4_6', 'pemimpin_4_7',
    'bersih_5_1', 'bersih_5_2', 'bersih_5_3', 'bersih_5_4', 'bersih_5_5', 'bersih_5_6', 'bersih_5_7', 'bersih_5_8', 'bersih_5_9', 'bersih_5_10', 'bersih_5_11',
    'mandiri_6_1', 'mandiri_6_2', 'mandiri_6_3', 'mandiri_6_4', 'mandiri_6_5', 'mandiri_6_6')
    def _nilai_total(self):
        for o in self:

            tauhid = sum([int(x) for x in [self.tauhid_1_1, self.tauhid_1_2, self.tauhid_1_3, self.tauhid_1_4, self.tauhid_1_5, self.tauhid_1_6, self.tauhid_1_7, self.tauhid_1_8]])
            orangtua = sum([int(x) for x in [self.orangtua_2_1, self.orangtua_2_2, self.orangtua_2_3, self.orangtua_2_4, self.orangtua_2_5]])
            disiplin = sum([int(x) for x in [self.disiplin_3_1, self.disiplin_3_2, self.disiplin_3_3, self.disiplin_3_4, self.disiplin_3_5, self.disiplin_3_6, self.disiplin_3_7]])
            pemimpin = sum([int(x) for x in [self.pemimpin_4_1, self.pemimpin_4_2, self.pemimpin_4_3, self.pemimpin_4_4, self.pemimpin_4_5, self.pemimpin_4_6, self.pemimpin_4_7]])
            bersih = sum([int(x) for x in [self.bersih_5_1, self.bersih_5_2, self.bersih_5_3, self.bersih_5_4, self.bersih_5_5, self.bersih_5_6, self.bersih_5_7, self.bersih_5_8, self.bersih_5_9, self.bersih_5_10, self.bersih_5_11]])
            mandiri = sum([int(x) for x in [self.mandiri_6_1, self.mandiri_6_2, self.mandiri_6_3, self.mandiri_6_4, self.mandiri_6_5, self.mandiri_6_6]])
            total = tauhid + orangtua + disiplin + pemimpin + bersih + mandiri

            o.update({
                'nilai_tauhid': tauhid,
                'nilai_orangtua': orangtua,
                'nilai_disiplin': disiplin,
                'nilai_pemimpin': pemimpin,
                'nilai_bersih': bersih,
                'nilai_mandiri': mandiri,
                'total_nilai': total
            })

    @api.depends('total_nilai')
    def _nilai_rata(self):
        for o in self:
            avg = o.total_nilai
            adab_ids = self.env['observasi.adab'].search([('period_id', '=', o.period_id.id)])
            if adab_ids :
                avg = sum(adab_ids.mapped('total_nilai')) / len(adab_ids)

            o.update({
                'total_avg': avg
            })
