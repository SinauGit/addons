from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

PEKAN = [
('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'),
('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), ('21', '21'), ('22', '22')
]

BULAN = [
('Januari', 'Januari'), ('Februari', 'Februari'), ('Maret', 'Maret'), ('April', 'April'), ('Mei', 'Mei'), ('Juni', 'Juni'),
('Juli', 'Juli'), ('Agustus', 'Agustus'), ('September', 'September'), ('Oktober', 'Oktober'), ('November', 'November'), ('Desember', 'Desember')
]

JENIS_KEGIATAN = [
    ('KBM_Efektif', 'KBM Efektif'),
    ('Persiapan_UKJ', 'Persiapan UKJ'),
    ('Persiapan_UAS', 'Persiapan UAS'),
    ('Jeda_Semester', 'Jeda Semester'),
    ('Assesment', 'Assesment'),
    ('Tidak_Masuk_Sekolah', 'Tidak Masuk Sekolah'),
]

LEMBAGA = [('KB', 'KB'), ('TK', 'TK'), ('SD', 'SD'), ('SMP', 'SMP'), ('SMA', 'SMA')]

class kalender_akademik(models.Model):
    _name = 'kalender.akademik'
    _description = 'Kalender Akademik'
    _order = 'name desc'

    name = fields.Char(string='No. Dokumen', default='/', required=True, readonly=True)
    lembaga = fields.Selection(LEMBAGA, string='Lembaga', required=True, default='SD', states={'Draft': [('readonly', False)]})
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    semester = fields.Selection([('Gasal', 'Gasal'), ('Genap', 'Genap')], string='Semester', required=True, default='Gasal', readonly=True, states={'Draft': [('readonly', False)]})
    pekan = fields.Selection(PEKAN, string='Pekan', required=True, default='1', readonly=True, states={'Draft': [('readonly', False)]})
    bulan = fields.Selection(BULAN, string='Bulan', required=True, default='Januari', readonly=True, states={'Draft': [('readonly', False)]})
    tgl_awal = fields.Date(string='Tanggal Awal', required=True, readonly=True, states={'Draft': [('readonly', False)]}, default=fields.Date.today)
    tgl_akhir = fields.Date(string='Tanggal Akhir', required=True, readonly=True, states={'Draft': [('readonly', False)]}, default=fields.Date.today)
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('In_Progress', 'In Progress'),
        ('Done', 'Done'),
    ], string='Status', readonly=True, copy=False, default='Draft')

    @api.multi
    def akademik_open(self):
        return self.write({'state': 'In_Progress'})

    @api.multi
    def akademik_draft(self):
        return self.write({'state': 'Draft'})

    @api.multi
    def akademik_done(self):
        return self.write({'state': 'Done'})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('kalender.akademik')
        return super(kalender_akademik, self).create(vals)

    @api.multi
    def unlink(self):
        for o in self:
            if o.state != 'Draft':
                raise UserError(("Kalender Akademik tidak bisa dihapus pada state %s !") % (o.state))
        return super(kalender_akademik, self).unlink()


    @api.multi
    def name_get(self):
        result = []
        for o in self:
            name = 'Pekan ' + o.pekan + ' # ' + o.tgl_awal.strftime("%d-%m-%Y") + ' # ' + o.tgl_akhir.strftime("%d-%m-%Y")
            result.append((o.id, name))
        return result


class penugasan_guru(models.Model):
    _name = 'penugasan.guru'
    _description = 'Penugasan Guru'
    _order = 'name desc'

    @api.depends('halaqah_line')
    def _get_halaqah(self):
        for x in self:
            x.update({
                'halaqah_count': len(set(x.halaqah_line.ids)),
            })

    @api.multi
    def action_view_halaqah(self):
        halaqah_ids = self.mapped('halaqah_line')
        action = self.env.ref('aa_kurikulum.pembagian_halaqah_action').read()[0]
        if len(halaqah_ids) > 1:
            action['domain'] = [('id', 'in', halaqah_ids.ids)]
        elif len(halaqah_ids) == 1:
            form_view = [(self.env.ref('aa_kurikulum.pembagian_halaqah_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = halaqah_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


    name = fields.Char(string='No. Dokumen', default='/', required=True, readonly=True)
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    lembaga = fields.Selection(LEMBAGA, string='Lembaga', required=True, states={'Draft': [('readonly', False)]})
    guru_id = fields.Many2one('hr.employee', 'Guru', required=True, domain="[('lembaga', '=', lembaga)]", readonly=True, states={'Draft': [('readonly', False)]})
    bidang_guru = fields.Selection([('Tahfizh', 'Tahfizh'), ('Umum', 'Umum'), ('Diniyah', 'Diniyah'), ('Centra', 'Centra')], string='Bidang Guru', required=True, default='Tahfizh', readonly=True, states={'Draft': [('readonly', False)]})
    kelas_id = fields.Many2one('master.kelas', 'Rombel', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    grade = fields.Selection([
                            ('A', 'A'), ('B', 'B'),
                            ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'),
                            ('7', '7'), ('8', '8'), ('9', '9'),
                            ('10', '10'), ('11', '11'), ('12', '12')
                            ], string='Grade', related='kelas_id.grade')
    wali_kelas = fields.Boolean('Wali Kelas ?')
    penguji = fields.Boolean('Penguji ?')
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('In_Progress', 'In Progress'),
        ('Done', 'Done'),
    ], string='Status', readonly=True, copy=False, default='Draft')

    halaqah_count = fields.Integer(string='Halaqah Count', compute='_get_halaqah')
    halaqah_line = fields.One2many('pembagian.halaqah', 'penugasan_guru_id', string='Halaqah', readonly=True)


    @api.multi
    def penugasan_open(self):
        return self.write({'state': 'In_Progress'})

    @api.multi
    def penugasan_draft(self):
        return self.write({'state': 'Draft'})

    @api.multi
    def penugasan_done(self):
        return self.write({'state': 'Done'})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('penugasan.guru')
        return super(penugasan_guru, self).create(vals)

    @api.multi
    def unlink(self):
        for o in self:
            if o.state != 'Draft':
                raise UserError(("Penugasan Guru tidak bisa dihapus pada state %s !") % (o.state))
        return super(penugasan_guru, self).unlink()

    @api.multi
    def name_get(self):
        result = []
        for tugas in self:
            name = '[' + tugas.name + '] ' + tugas.guru_id.name
            result.append((tugas.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        guru_ids = []
        if name:
            guru_ids = self._search([('guru_id.name', operator, name)] + args, limit=limit, access_rights_uid=name_get_uid)
        if not guru_ids:
            guru_ids = self._search([('name', operator, name)] + args, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(guru_ids).name_get()


class daftar_surat(models.Model):
    _name = 'daftar.surat'
    _description = 'Daftar Surat'
    _order = 'code desc'

    code = fields.Integer(string='No', required=True)
    name = fields.Char(string='Nama', required=True)
    arti = fields.Char(string='Terjemah', required=True)
    ayat = fields.Integer(string='Jumlah Ayat', required=True)
    tempat = fields.Char(string='Tempat', required=True)
    juz = fields.Integer(string='Juz', required=True)
    kuadran = fields.Selection([('K1', 'K1'), ('K2', 'K2'), ('K3', 'K3'), ('K4', 'K4'), ('K5', 'K5'), ('K6', 'K6'), ('K7', 'K7'), ('K8', 'K8')], string='Materi Kuadran SD', required=True, default='K1')
    kuadran_tk = fields.Selection([('K1', 'K1'), ('K2', 'K2'), ('K3', 'K3'), ('K4', 'K4'), ('K5', 'K5'), ('K6', 'K6'), ('K7', 'K7'), ('K8', 'K8')], string='Materi Kuadran TK', required=True, default='K1')
    active = fields.Boolean(default=True)


    # @api.multi
    # def update_code(self):
    #     for o in self:
    #         for x in self.search([]):
    #             x.code = x.id

    @api.multi
    def name_get(self):
        result = []
        for surat in self:
            name = '[' + str(surat.code) + '] ' + surat.name + ' # ' + str(surat.ayat) + ' # ' + str(surat.juz) # + ' # ' + surat.kuadran
            result.append((surat.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        surat_ids = []
        if name:
            surat_ids = self._search([('code', operator, name)] + args, limit=limit, access_rights_uid=name_get_uid)
        if not surat_ids:
            surat_ids = self._search([('name', operator, name)] + args, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(surat_ids).name_get()


class pembagian_halaqah(models.Model):
    _name = 'pembagian.halaqah'
    _description = 'Pembagian Halaqah'
    _order = 'kelas_id, siswa_id'

    @api.depends('lp_tahfidz_line')
    def _get_lp_tahfidz(self):
        for x in self:
            x.update({
                'lp_tahfidz_count': len(set(x.lp_tahfidz_line.ids)),
            })

    @api.multi
    def action_view_lp_tahfidz(self):
        lp_tahfidz_ids = self.mapped('lp_tahfidz_line')
        action = self.env.ref('aa_kurikulum.lesson_plan_action').read()[0]
        if len(lp_tahfidz_ids) > 1:
            action['domain'] = [('id', 'in', lp_tahfidz_ids.ids)]
        elif len(lp_tahfidz_ids) == 1:
            form_view = [(self.env.ref('aa_kurikulum.lesson_plan_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = lp_tahfidz_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


    @api.depends('kbm_tahfidz_line')
    def _get_kbm_tahfidz(self):
        for x in self:
            x.update({
                'kbm_tahfidz_count': len(set(x.kbm_tahfidz_line.ids)),
            })

    @api.multi
    def action_view_kbm_tahfidz(self):
        kbm_tahfidz_ids = self.mapped('kbm_tahfidz_line')
        action = self.env.ref('aa_kurikulum.kbm_tahfidz_action').read()[0]
        if len(kbm_tahfidz_ids) > 1:
            action['domain'] = [('id', 'in', kbm_tahfidz_ids.ids)]
        elif len(kbm_tahfidz_ids) == 1:
            form_view = [(self.env.ref('aa_kurikulum.kbm_tahfidz_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = kbm_tahfidz_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


    name = fields.Char(string='No. Dokumen', default='/', required=True, readonly=True)
    user_id = fields.Many2one('res.users', string='User', related='penugasan_guru_id.guru_id.user_id')
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', related='penugasan_guru_id.fiscalyear_id')
    lembaga = fields.Selection(LEMBAGA, string='Lembaga', related='penugasan_guru_id.lembaga')
    kelas_id = fields.Many2one('master.kelas', 'Rombel', related='penugasan_guru_id.kelas_id')
    siswa_id = fields.Many2one('res.partner', 'Siswa', required=True, domain="[('student', '=', True), ('class_id', '=', kelas_id)]", readonly=True, states={'Draft': [('readonly', False)]})
    penugasan_guru_id = fields.Many2one('penugasan.guru', 'Guru Halaqah', required=True, domain=[('state', '=', 'In_Progress')], readonly=True, states={'Draft': [('readonly', False)]})
    surat_id = fields.Many2one('daftar.surat', 'Surat Terakhir', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    ayat = fields.Integer('Ayat Terakhir', readonly=True, states={'Draft': [('readonly', False)]})
    indeks = fields.Char(string='Index Hafalan', default='4 baris/pekan', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    surat_awal_id = fields.Many2one('daftar.surat', 'Materi Awal', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    surat_akhir_id = fields.Many2one('daftar.surat', 'Materi Akhir', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('In_Progress', 'In Progress'),
        ('Done', 'Done'),
    ], string='Status', readonly=True, copy=False, default='Draft')

    lp_tahfidz_count = fields.Integer(string='LP Tahfidz Count', compute='_get_lp_tahfidz')
    kbm_tahfidz_count = fields.Integer(string='KBM Tahfidz Count', compute='_get_kbm_tahfidz')

    lp_tahfidz_line = fields.One2many('lesson.plan', 'halaqah_id', string='Lesson Plan Tahfidz', readonly=True)
    kbm_tahfidz_line = fields.One2many('kbm.tahfidz', 'halaqah_id', string='KBM Tahfidz', readonly=True)

    @api.multi
    def halaqah_open(self):
        for lp in self.lp_tahfidz_line:
            lp.user_id = self.penugasan_guru_id.guru_id.user_id.id
        for kbm in self.kbm_tahfidz_line:
            kbm.user_id = self.penugasan_guru_id.guru_id.user_id.id
            
        return self.write({'state': 'In_Progress'})

    @api.multi
    def halaqah_draft(self):
        return self.write({'state': 'Draft'})

    @api.multi
    def halaqah_done(self):
        return self.write({'state': 'Done'})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('pembagian.halaqah')
        return super(pembagian_halaqah, self).create(vals)

    @api.multi
    def unlink(self):
        for o in self:
            if o.state != 'Draft':
                raise UserError(("Pembagian Halaqah tidak bisa dihapus pada state %s !") % (o.state))
        return super(pembagian_halaqah, self).unlink()

    @api.multi
    def name_get(self):
        result = []
        for o in self:
            name = str(o.penugasan_guru_id.guru_id.name) + ' # ' + str(o.siswa_id.name) + ' # ' + str(o.kelas_id.name) # + o.lembaga.upper() + ' # '
            result.append((o.id, name))
        return result

    @api.multi
    def create_lp_tahfidz(self):
        action = self.env.ref('aa_kurikulum.lesson_plan_action').read()[0]
        action['domain'] = [('halaqah_id', '=', self.id)]
        action['views'] = [(self.env.ref('aa_kurikulum.lesson_plan_view_form').id, 'form')]
        action['context'] = {
                'default_surat_awal_id': self.surat_awal_id.id,
                'default_surat_akhir_id':self.surat_akhir_id.id,
                'default_halaqah_id': self.id
        }
        return action

    @api.multi
    def create_kbm_tahfidz(self):
        action = self.env.ref('aa_kurikulum.kbm_tahfidz_action').read()[0]
        action['domain'] = [('halaqah_id', '=', self.id)]
        action['views'] = [(self.env.ref('aa_kurikulum.kbm_tahfidz_view_form').id, 'form')]
        action['context'] = {
                'default_surat_awal_id': self.surat_awal_id.id,
                'default_surat_akhir_id':self.surat_akhir_id.id,
                'default_halaqah_id': self.id
        }
        return action
             

class lesson_plan(models.Model):
    _name = 'lesson.plan'
    _description = 'Lesson Plan Tahfidz'
    _order = 'name desc'

    name = fields.Char(string='No. Dokumen', default='/', required=True, readonly=True)
    user_id = fields.Many2one('res.users', string='User', readonly=True, required=True, default=lambda self: self.env.user, copy=False)
    halaqah_id = fields.Many2one('pembagian.halaqah', 'Halaqah', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    kalender_id = fields.Many2one('kalender.akademik', 'Pekan KBM', required=True, domain=[('state', '=', 'In_Progress')], readonly=True, states={'Draft': [('readonly', False)]})
    siswa_id = fields.Many2one('res.partner', 'Siswa', related='halaqah_id.siswa_id')
    surat_awal_id = fields.Many2one('daftar.surat', 'Surat Awal', readonly=True, states={'Draft': [('readonly', False)]})
    ayat_awal = fields.Integer('Ayat Awal', readonly=True, states={'Draft': [('readonly', False)]})
    surat_akhir_id = fields.Many2one('daftar.surat', 'Surat Akhir', readonly=True, states={'Draft': [('readonly', False)]})
    ayat_akhir = fields.Integer('Ayat Akhir', readonly=True, states={'Draft': [('readonly', False)]})
    target_baris = fields.Integer('Target Baris', readonly=True, states={'Draft': [('readonly', False)]})
    notes = fields.Char(string='Catatan Guru', readonly=True, states={'Draft': [('readonly', False)]})
    kegiatan = fields.Selection(JENIS_KEGIATAN, string='Kegiatan', default='KBM_Efektif', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('In_Progress', 'In Progress'),
        ('Done', 'Done'),
    ], string='Status', readonly=True, copy=False, default='Draft')

    @api.multi
    def lesson_open(self):
        return self.write({'state': 'In_Progress'})

    @api.multi
    def lesson_draft(self):
        return self.write({'state': 'Draft'})

    @api.multi
    def lesson_done(self):
        return self.write({'state': 'Done'})

    @api.model
    def create(self, vals):
        if vals['kegiatan'] == 'KBM_Efektif':
            if not vals['target_baris']:
                raise UserError(("Target baris tidak boleh 0 !"))
            elif not vals['ayat_awal']:
                raise UserError(("Ayat awal tidak boleh 0 !"))
            elif not vals['ayat_akhir']:
                raise UserError(("Ayat akhir tidak boleh 0 !"))
        vals['name'] = self.env['ir.sequence'].next_by_code('lesson.plan')
        return super(lesson_plan, self).create(vals)

    @api.multi
    def unlink(self):
        for o in self:
            if o.state != 'Draft':
                raise UserError(("Lesson Plan tidak bisa dihapus pada state %s !") % (o.state))
        return super(lesson_plan, self).unlink()


    @api.onchange('user_id', 'halaqah_id')
    def halaqah_id_change(self):
        return {
                'domain': {
                            'surat_awal_id': [('id', 'in', [x for x in range(self.halaqah_id.surat_akhir_id.id, self.halaqah_id.surat_awal_id.id+1)])],
                            'surat_akhir_id': [('id', 'in', [x for x in range(self.halaqah_id.surat_akhir_id.id, self.halaqah_id.surat_awal_id.id+1)])],
                            'halaqah_id' : [('penugasan_guru_id.guru_id.user_id', '=', self.user_id.id), ('state', '=', 'In_Progress')]
                            }
                }

    _sql_constraints = [
            ('unique_lesson_plan_id', 'UNIQUE(halaqah_id, kalender_id)', 'LP untuk pekan tersebut sudah pernah diisi  !')
    ]


class kbm_tahfidz(models.Model):
    _name = 'kbm.tahfidz'
    _description = 'KBM Tahfidz'
    _order = 'kalender_id'

    name = fields.Char(string='No. Dokumen', default='/', required=True, readonly=True)
    user_id = fields.Many2one('res.users', string='User', readonly=True, required=True, default=lambda self: self.env.user, copy=False)
    halaqah_id = fields.Many2one('pembagian.halaqah', 'Halaqah', required=True, domain=[('state', '=', 'In_Progress')], readonly=True, states={'Draft': [('readonly', False)]})
    kalender_id = fields.Many2one('kalender.akademik', 'Pekan KBM', required=True, domain=[('state', '=', 'In_Progress')], readonly=True, states={'Draft': [('readonly', False)]})
    siswa_id = fields.Many2one('res.partner', 'Siswa', related='halaqah_id.siswa_id', store=True)
    surat_awal_id = fields.Many2one('daftar.surat', 'Surat Awal', readonly=True, states={'Draft': [('readonly', False)]})
    ayat_awal = fields.Integer('Ayat Awal', required=True, readonly=True, states={'Draft': [('readonly', False)]}, default=0)
    surat_akhir_id = fields.Many2one('daftar.surat', 'Surat Akhir', readonly=True, states={'Draft': [('readonly', False)]})
    ayat_akhir = fields.Integer('Ayat Akhir', required=True, readonly=True, states={'Draft': [('readonly', False)]}, default=0)
    jumlah_ayat = fields.Integer('Jumlah Ayat', required=True, readonly=True, states={'Draft': [('readonly', False)]}, default=0)
    jumlah_baris = fields.Integer('Jumlah Baris', required=True, readonly=True, states={'Draft': [('readonly', False)]}, default=0)
    murojaah = fields.Char(string="Muroja'ah", readonly=True, states={'Draft': [('readonly', False)]})
    bbq = fields.Char(string='BBQ Tilawah', readonly=True, states={'Draft': [('readonly', False)]})
    notes = fields.Char(string='Catatan Guru', readonly=True, states={'Draft': [('readonly', False)]})
    kegiatan = fields.Selection(JENIS_KEGIATAN, string='Kegiatan', default='KBM_Efektif', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    juz = fields.Integer(string='Juz', related='surat_awal_id.juz', store=True)
    kuadran = fields.Selection([('K1', 'K1'), ('K2', 'K2'), ('K3', 'K3'), ('K4', 'K4'), ('K5', 'K5'), ('K6', 'K6'), ('K7', 'K7'), ('K8', 'K8')], string='Materi Kuadran SD', related='surat_awal_id.kuadran', store=True)
    kuadran_tk = fields.Selection([('K1', 'K1'), ('K2', 'K2'), ('K3', 'K3'), ('K4', 'K4'), ('K5', 'K5'), ('K6', 'K6'), ('K7', 'K7'), ('K8', 'K8')], string='Materi Kuadran TK', related='surat_awal_id.kuadran_tk', store=True)
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('In_Progress', 'In Progress'),
        ('Done', 'Done'),
    ], string='Status', readonly=True, copy=False, default='Draft')

    @api.multi
    def kbm_open(self):
        return self.write({'state': 'In_Progress'})

    @api.multi
    def kbm_draft(self):
        return self.write({'state': 'Draft'})

    @api.multi
    def kbm_done(self):
        return self.write({'state': 'Done'})

    @api.model
    def create(self, vals):
        if vals['kegiatan'] == 'KBM_Efektif':
            if not vals['jumlah_ayat']:
                raise UserError(("Jumlah ayat tidak boleh 0 !"))
            elif not vals['jumlah_baris']:
                raise UserError(("Jumlah baris tidak boleh 0 !"))
            elif not vals['ayat_awal']:
                raise UserError(("Ayat awal tidak boleh 0 !"))
            elif not vals['ayat_akhir']:
                raise UserError(("Ayat akhir tidak boleh 0 !"))
        vals['name'] = self.env['ir.sequence'].next_by_code('kbm.tahfidz')
        return super(kbm_tahfidz, self).create(vals)

    @api.multi
    def unlink(self):
        for o in self:
            if o.state != 'Draft':
                raise UserError(("KBM Tahfidz tidak bisa dihapus pada state %s !") % (o.state))
        return super(kbm_tahfidz, self).unlink()

    @api.onchange('user_id', 'halaqah_id')
    def halaqah_id_change(self):
        return {
                'domain': {
                            'surat_awal_id': [('id', 'in', [x for x in range(self.halaqah_id.surat_akhir_id.id, self.halaqah_id.surat_awal_id.id+1)])],
                            'surat_akhir_id': [('id', 'in', [x for x in range(self.halaqah_id.surat_akhir_id.id, self.halaqah_id.surat_awal_id.id+1)])],
                            'halaqah_id' : [('penugasan_guru_id.guru_id.user_id', '=', self.user_id.id), ('state', '=', 'In_Progress')]
                            }
                }


    _sql_constraints = [
            ('unique_kbm_tahfidz_id', 'UNIQUE(halaqah_id, kalender_id)', 'KBM untuk pekan tersebut sudah pernah diisi !')
    ]


class permohonan_ukj(models.Model):
    _name = 'permohonan.ukj'
    _description = 'Surat Permohonan UKJ'
    _order = 'name desc'

    name = fields.Char(string='No. Dokumen', default='/', required=True, readonly=True)
    tanggal = fields.Date('Tanggal', required=True, default=fields.Date.context_today, readonly=True, states={'Draft': [('readonly', False)]})
    tanggal_revisi = fields.Date('Tanggal', readonly=True, states={'Approved_PIC': [('readonly', False)]})
    alasan_revisi = fields.Char(string='Alasan', readonly=True, states={'Approved_PIC': [('readonly', False)]})
    tanggal_approve_pic = fields.Date('PIC Tahfidz', readonly=True)
    tanggal_approve_ortu = fields.Date('Wali Murid', readonly=True)
    user_id = fields.Many2one('res.users', string='Musyrif/ah', readonly=True, required=True, default=lambda self: self.env.user, copy=False)
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    lembaga = fields.Selection(LEMBAGA, string='Lembaga', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    kelas_id = fields.Many2one('master.kelas', 'Rombel', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    siswa_id = fields.Many2one('res.partner', 'Siswa', required=True, domain="[('student', '=', True)]", readonly=True, states={'Draft': [('readonly', False)]}, ondelete='cascade')
    juz = fields.Integer(string='Materi UKJ', readonly=True, states={'Draft': [('readonly', False)]})
    jumlah_surat = fields.Integer('Jumlah Surat', readonly=True, states={'Draft': [('readonly', False)]})
    persiapan = fields.Integer(string='Persiapan UKJ (Hari)', readonly=True, states={'Draft': [('readonly', False)]})
    tanggal_mulai_persiapan = fields.Date('Mulai Persiapan', required=True, default=fields.Date.context_today, readonly=True, states={'Draft': [('readonly', False)]})
    pukul_awal = fields.Float(string='Pukul', readonly=True, states={'Draft': [('readonly', False)]})
    pukul_akhir = fields.Float(string='Pukul', readonly=True, states={'Draft': [('readonly', False)]})
    permohonan_line = fields.One2many('permohonan.ukj.line', 'permohonan_id', 'LP UKJ')
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('Approved_PIC', 'Approved by PIC Tahfizh'),
        ('Approved_Wali', 'Approved by Ortu/Wali'),
        ('Done', 'Done'),
    ], string='Status', readonly=True, copy=False, default='Draft')

    @api.onchange('kelas_id', 'lembaga', 'fiscalyear_id', 'siswa_id')
    def onchange_siswa(self):
        if self.siswa_id:
            self.update({'kelas_id': self.siswa_id.class_id.id, 'lembaga': self.siswa_id.lembaga, 'fiscalyear_id': self.siswa_id.fiscalyear_id.id})
        else:
            self.update({'kelas_id': False, 'lembaga': False, 'fiscalyear_id': False})

    @api.multi
    def permohonan_open_pic(self):
        if self.persiapan <= 0:
            raise UserError(("Kolom Persiapan UKJ belum diisi !"))

        if not self.permohonan_line:
            tgl = self.tanggal_mulai_persiapan
            for x in range(self.persiapan):
                self.env['permohonan.ukj.line'].create({
                                'permohonan_id': self.id,
                                'name': tgl,
                })
                tgl += timedelta(days=1)

        return self.write({'state': 'Approved_PIC', 'tanggal_approve_pic': datetime.today()})

    @api.multi
    def permohonan_open_ortu(self):
        return self.write({'state': 'Approved_Wali', 'tanggal_approve_ortu': datetime.today()})

    @api.multi
    def permohonan_draft(self):
        # if self.permohonan_line:
        #     self.permohonan_line.unlink()
        return self.write({'state': 'Draft', 'tanggal_approve_pic': False, 'tanggal_approve_ortu': False})

    @api.multi
    def permohonan_done(self):
        return self.write({'state': 'Done'})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('permohonan.ukj')
        return super(permohonan_ukj, self).create(vals)

    # @api.multi
    # def unlink(self):
    #     for o in self:
    #         if o.state != 'Draft':
    #             raise UserError(("Permohonan UKJ tidak bisa dihapus pada state %s !") % (o.state))
    #     return super(permohonan_ukj, self).unlink()
    #
    # @api.multi
    # def name_get(self):
    #     result = []
    #     for o in self:
    #         name = o.siswa_id.name + ' # ' + o.lembaga.upper() + ' # ' + o.kelas_id.name
    #         result.append((o.id, name))
    #     return result


class permohonan_ukj_line(models.Model):
    _name = "permohonan.ukj.line"
    _description = 'LP UKJ'

    permohonan_id = fields.Many2one('permohonan.ukj', 'Permohonan UKJ', required=True, ondelete='cascade')
    name = fields.Date('Tanggal', readonly=True, states={'Approved_Wali': [('readonly', False)]})
    sekolah = fields.Char('Kegiatan di Sekolah', required=True, readonly=True, states={'Approved_Wali': [('readonly', False)]}, default='-')
    rumah = fields.Char('Kegiatan di Rumah', required=True, readonly=True, states={'Approved_Wali': [('readonly', False)]}, default='-')
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('Approved_PIC', 'Approved by PIC Tahfizh'),
        ('Approved_Wali', 'Approved by Ortu/Wali'),
        ('Done', 'Done'),
    ], string='Status', related='permohonan_id.state')


    @api.depends('name')
    def set_day(self):
        for o in self:
            if o.name:
                o.day = o.name.strftime("%A")

    day = fields.Selection([
        ('Monday', 'Senin'),
        ('Tuesday', 'Selasa'),
        ('Wednesday', 'Rabu'),
        ('Thursday', 'Kamis'),
        ('Friday', 'Jumat'),
        ('Saturday', 'Sabtu'),
        ('Sunday', 'Ahad'),
        ], string='Hari', store=True, compute=set_day)

class ujian_kenaikan_juz(models.Model):
    _name = 'ujian.kenaikan.juz'
    _description = 'Ujian Kenaikan Juz'
    _order = 'name desc'

    name = fields.Char(string='No. Dokumen', default='/', required=True, readonly=True)
    tanggal = fields.Date('Tanggal', required=True, default=fields.Date.context_today, readonly=True, states={'Draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users', string='Musyrif/ah', readonly=True, required=True, default=lambda self: self.env.user, copy=False)
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    lembaga = fields.Selection(LEMBAGA, string='Lembaga', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    kelas_id = fields.Many2one('master.kelas', 'Rombel', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    jenis = fields.Selection([('Juz', 'Juz'), ('Komprehensif', 'Komprehensif')], string='Jenis', default='Juz', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    siswa_id = fields.Many2one('res.partner', 'Siswa', required=True, domain="[('student', '=', True)]", readonly=True, states={'Draft': [('readonly', False)]})
    juz = fields.Char(string='Ujian Juz', readonly=True, states={'Draft': [('readonly', False)]})
    tanbih_kelancaran = fields.Integer(string='Tanbih', readonly=True, states={'Draft': [('readonly', False)]})
    bantuan_kelancaran = fields.Integer(string='Bantuan', readonly=True, states={'Draft': [('readonly', False)]})
    nilai_kelancaran = fields.Integer(string='Nilai Akhir', compute='_nilai_akhir', store=True)
    tanbih_gunnah = fields.Integer(string='Tanbih', readonly=True, states={'Draft': [('readonly', False)]})
    bantuan_gunnah = fields.Integer(string='Bantuan', readonly=True, states={'Draft': [('readonly', False)]})
    nilai_gunnah = fields.Integer(string='Nilai Akhir', compute='_nilai_akhir', store=True)
    tanbih_mad = fields.Integer(string='Tanbih', readonly=True, states={'Draft': [('readonly', False)]})
    bantuan_mad = fields.Integer(string='Bantuan', readonly=True, states={'Draft': [('readonly', False)]})
    nilai_mad = fields.Integer(string='Nilai Akhir', compute='_nilai_akhir', store=True)
    tanbih_makhroj = fields.Integer(string='Tanbih', readonly=True, states={'Draft': [('readonly', False)]})
    bantuan_makhroj = fields.Integer(string='Bantuan', readonly=True, states={'Draft': [('readonly', False)]})
    nilai_makhroj = fields.Integer(string='Nilai Akhir', compute='_nilai_akhir', store=True)
    surat_line = fields.One2many('surat.ukj.line', 'kenaikan_id', 'Daftar Surat UKJ', states={'Done': [('readonly', True)]})
    total_nilai = fields.Integer(string='Nilai', compute='_nilai_predikat', store=True)
    predikat = fields.Char(string='Predikat', compute='_nilai_predikat', store=True)
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('In_Progress', 'In Progress'),
        ('Done', 'Done'),
    ], string='Status', readonly=True, copy=False, default='Draft')


    @api.onchange('kelas_id', 'lembaga', 'fiscalyear_id', 'siswa_id')
    def onchange_siswa(self):
        if self.siswa_id:
            self.update({'kelas_id': self.siswa_id.class_id.id, 'lembaga': self.siswa_id.lembaga, 'fiscalyear_id': self.siswa_id.fiscalyear_id.id})
        else:
            self.update({'kelas_id': False, 'lembaga': False, 'fiscalyear_id': False})

    @api.depends('bantuan_kelancaran', 'bantuan_gunnah', 'bantuan_mad', 'bantuan_makhroj')
    def _nilai_akhir(self):
        for o in self:
            kelancaran = 40; gunnah = 20; mad = 20; makhroj = 20
            o.update({
                'nilai_kelancaran': kelancaran - self.bantuan_kelancaran,
                'nilai_gunnah': gunnah - self.bantuan_gunnah,
                'nilai_mad': mad - self.bantuan_mad,
                'nilai_makhroj': makhroj - self.bantuan_makhroj,
            })

    @api.depends('nilai_kelancaran', 'nilai_gunnah', 'nilai_mad', 'nilai_makhroj')
    def _nilai_predikat(self):
        for o in self:
            predikat = 'Mumtaz'
            total = self.nilai_kelancaran + self.nilai_gunnah + self.nilai_mad + self.nilai_makhroj

            if  90 <= total <= 99:
                predikat = 'Zayyid Ziddan'
            elif 80 <= total <= 89:
                predikat = 'Zayyid'
            elif 70 <= total <= 79:
                predikat = 'Ahsan'
            elif 60 <= total <= 69:
                predikat = 'Maqbul'
            elif total <= 59:
                predikat = 'Rosib'

            o.update({
                'total_nilai': total,
                'predikat' : predikat
            })

    @api.multi
    def kenaikan_open(self):
        return self.write({'state': 'In_Progress'})

    @api.multi
    def kenaikan_draft(self):
        return self.write({'state': 'Draft'})

    @api.multi
    def kenaikan_done(self):
        return self.write({'state': 'Done'})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('ujian.kenaikan.juz')
        return super(ujian_kenaikan_juz, self).create(vals)

    # @api.multi
    # def unlink(self):
    #     for o in self:
    #         if o.state != 'Draft':
    #             raise UserError(("Doc UKJ tidak bisa dihapus pada state %s !") % (o.state))
    #     return super(ujian_kenaikan_juz, self).unlink()
    #
    # @api.multi
    # def name_get(self):
    #     result = []
    #     for o in self:
    #         name = o.siswa_id.name + ' # ' + o.lembaga.upper() + ' # ' + o.kelas_id.name
    #         result.append((o.id, name))
    #     return result

class surat_ukj_line(models.Model):
    _name = 'surat.ukj.line'
    _description = 'Daftar Surat UKJ'

    kenaikan_id = fields.Many2one('ujian.kenaikan.juz', 'Ujian Kenaikan Juz', required=True, ondelete='cascade')
    name = fields.Many2one('daftar.surat', 'Surat', required=True)
    tanbih = fields.Char('Tanbih (Ayat)')
    teguran = fields.Char('Bantuan (Ayat)')


class tahfidz_akhir_semester(models.Model):
    _name = 'tahfidz.akhir.semester'
    _description = 'Evaluasi Tahfidz Akhir Semester'
    _order = 'name desc'

    name = fields.Char(string='No. Dokumen', default='/', required=True, readonly=True)
    tanggal = fields.Date('Tanggal', required=True, default=fields.Date.context_today, readonly=True, states={'Draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users', string='Musyrif/ah', readonly=True, required=True, default=lambda self: self.env.user, copy=False)
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    lembaga = fields.Selection(LEMBAGA, string='Lembaga', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    kelas_id = fields.Many2one('master.kelas', 'Rombel', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    siswa_id = fields.Many2one('res.partner', 'Siswa', required=True, domain="[('student', '=', True)]", readonly=True, states={'Draft': [('readonly', False)]})
    halaqah_id = fields.Many2one('pembagian.halaqah', 'Halaqah', compute='_get_halaqah')
    semester = fields.Selection([('Gasal', 'Gasal'), ('Genap', 'Genap')], string='Semester', required=True, default='Gasal', readonly=True, states={'Draft': [('readonly', False)]})

    kegiatan_awal_id = fields.Many2one('daftar.surat', 'Kegiatan Menghafal Awal', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    kegiatan_akhir_id = fields.Many2one('daftar.surat', 'Kegiatan Menghafal Akhir', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    capai_awal_id = fields.Many2one('daftar.surat', 'Pencapaian Hafalan Awal', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    capai_akhir_id = fields.Many2one('daftar.surat', 'Pencapaian Hafalan Akhir', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    penguji_id = fields.Many2one('penugasan.guru', string='Penguji', domain=[('penguji', '=', 'True'), ('state', '=', 'In_Progress')], required=True, readonly=True, states={'Draft': [('readonly', False)]})

    target_hafalan = fields.Selection([('Tuntas', 'Tuntas'), ('Belum_Tuntas', 'Belum Tuntas')], string='Target Hafalan', readonly=True, states={'Draft': [('readonly', False)]})
    ujian_kenaikan_juz = fields.Selection([('Sudah', 'Sudah'), ('Belum', 'Belum')], string='Ujian Kenaikan juz', readonly=True, states={'Draft': [('readonly', False)]})
    kehadiran = fields.Selection([('50', '> 50%'), ('70', '> 70%'), ('90', '> 90%')], string='Kehadiran', readonly=True, states={'Draft': [('readonly', False)]})
    adab = fields.Selection([('Baik', 'Baik'), ('Cukup', 'Cukup'), ('Kurang', 'Kurang')], string='Adab Terhadap Al-Quran', readonly=True, states={'Draft': [('readonly', False)]})
    kesungguhan = fields.Selection([('Baik', 'Baik'), ('Cukup', 'Cukup'), ('Kurang', 'Kurang')], string='Kesungguhan Menghafal', readonly=True, states={'Draft': [('readonly', False)]})
    sikap = fields.Selection([('Baik', 'Baik'), ('Cukup', 'Cukup'), ('Kurang', 'Kurang')], string='Sikap Dalam Menghafal', readonly=True, states={'Draft': [('readonly', False)]})

    jumlah_surat = fields.Integer('Jumlah Surat Yang Diuji', compute='_nilai_predikat')
    total_nilai = fields.Integer('Total Nilai Seluruh Surat', compute='_nilai_predikat')
    nilai_uas = fields.Integer('Nilai UAS Tahfidz', compute='_nilai_predikat')
    predikat_umum = fields.Char('Predikat Umum (Total Nilai/Jumlah Surat)', compute='_nilai_predikat')

    surat_line = fields.One2many('surat.uas.line', 'evaluasi_id', 'Daftar Surat UAS', states={'Done': [('readonly', True)]})

    state = fields.Selection([
        ('Draft', 'Draft'),
        ('In_Progress', 'In Progress'),
        ('Done', 'Done'),
    ], string='Status', readonly=True, copy=False, default='Draft')


    @api.onchange('kelas_id', 'lembaga', 'fiscalyear_id', 'siswa_id')
    def onchange_siswa(self):
        if self.siswa_id:
            self.update({'kelas_id': self.siswa_id.class_id.id, 'lembaga': self.siswa_id.lembaga, 'fiscalyear_id': self.siswa_id.fiscalyear_id.id})
        else:
            self.update({'kelas_id': False, 'lembaga': False, 'fiscalyear_id': False})


    @api.multi
    def evaluasi_open(self):
        return self.write({'state': 'In_Progress'})

    @api.multi
    def evaluasi_draft(self):
        return self.write({'state': 'Draft'})

    @api.multi
    def evaluasi_done(self):
        return self.write({'state': 'Done'})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('tahfidz.akhir.semester')
        return super(tahfidz_akhir_semester, self).create(vals)


    @api.depends('siswa_id')
    def _get_halaqah(self):
        for o in self:
            if o.siswa_id :
                halaqah = self.env['pembagian.halaqah'].search([('siswa_id', '=', o.siswa_id.id), ('state', '=', 'In_Progress')], limit=1)
                o.update({
                    'halaqah_id': halaqah or False,
                })

    @api.depends('surat_line')
    def _nilai_predikat(self):
        for o in self:
            if o.surat_line :

                nilai = 0; surat = len(o.surat_line)
                for line in o.surat_line:
                    nilai += line.nilai_total

                predikat = 'Terampil'
                total = nilai/surat

                if 70 <= total <= 84:
                    predikat = 'Menguasai'
                elif 60 <= total <= 69:
                    predikat = 'Berkembang'
                elif total <= 59:
                    predikat = 'Tumbuh'

                o.update({
                    'jumlah_surat': surat,
                    'total_nilai': nilai,
                    'nilai_uas': nilai/surat,
                    'predikat_umum' : predikat
                })

    # @api.multi
    # def unlink(self):
    #     for o in self:
    #         if o.state != 'Draft':
    #             raise UserError(("Doc UKJ tidak bisa dihapus pada state %s !") % (o.state))
    #     return super(ujian_kenaikan_juz, self).unlink()
    #
    # @api.multi
    # def name_get(self):
    #     result = []
    #     for o in self:
    #         name = o.siswa_id.name + ' # ' + o.lembaga.upper() + ' # ' + o.kelas_id.name
    #         result.append((o.id, name))
    #     return result

class surat_uas_line(models.Model):
    _name = 'surat.uas.line'
    _description = 'Daftar Surat Evaluasi Tahfidz UAS'

    evaluasi_id = fields.Many2one('tahfidz.akhir.semester', 'Evaluasi Tahfidz Akhir Semester', required=True, ondelete='cascade')
    name = fields.Many2one('daftar.surat', 'Surat', required=True)

    letak_salah_kelancaran = fields.Char(string='Letak Ayat Yang Salah')
    jumlah_salah_kelancaran = fields.Integer(string='Jumlah Bantuan')
    nilai_kelancaran = fields.Integer(string='Nilai', compute='_nilai_akhir')

    letak_salah_gunnah = fields.Char(string='Letak Ayat Yang Salah')
    jumlah_salah_gunnah = fields.Integer(string='Jumlah Bantuan')
    nilai_gunnah = fields.Integer(string='Nilai', compute='_nilai_akhir')

    letak_salah_mad = fields.Char(string='Letak Ayat Yang Salah')
    jumlah_salah_mad = fields.Integer(string='Jumlah Bantuan')
    nilai_mad = fields.Integer(string='Nilai', compute='_nilai_akhir')

    letak_salah_makhroj = fields.Char(string='Letak Ayat Yang Salah')
    jumlah_salah_makhroj = fields.Integer(string='Jumlah Bantuan')
    nilai_makhroj = fields.Integer(string='Nilai', compute='_nilai_akhir')

    nilai_total = fields.Integer(string='Total', compute='_nilai_akhir')

    @api.depends('jumlah_salah_kelancaran', 'jumlah_salah_gunnah', 'jumlah_salah_mad', 'jumlah_salah_makhroj')
    def _nilai_akhir(self):
        for o in self:
            kelancaran = 40 - o.jumlah_salah_kelancaran
            gunnah = 20 - o.jumlah_salah_gunnah
            mad = 20 - o.jumlah_salah_mad
            makhroj = 20 - o.jumlah_salah_makhroj
            o.update({
                'nilai_kelancaran': kelancaran,
                'nilai_gunnah': gunnah,
                'nilai_mad': mad,
                'nilai_makhroj': makhroj,
                'nilai_total': kelancaran + gunnah + mad + makhroj
            })


class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.depends('lp_tahfidz_line')
    def _get_lp_tahfidz(self):
        for x in self:
            x.update({
                'lp_tahfidz_count': len(set(x.lp_tahfidz_line.ids)),
            })

    @api.depends('kbm_tahfidz_line')
    def _get_kbm_tahfidz(self):
        for x in self:
            x.update({
                'kbm_tahfidz_count': len(set(x.kbm_tahfidz_line.ids)),
            })

    @api.depends('mohon_ukj_tahfidz_count')
    def _get_mohon_ukj_tahfidz(self):
        for x in self:
            x.update({
                'mohon_ukj_tahfidz_count': len(set(x.mohon_ukj_tahfidz_line.ids)),
            })

    @api.depends('ukj_tahfidz_count')
    def _get_ukj_tahfidz(self):
        for x in self:
            x.update({
                'ukj_tahfidz_count': len(set(x.ukj_tahfidz_line.ids)),
            })

    @api.depends('uas_tahfidz_count')
    def _get_uas_tahfidz(self):
        for x in self:
            x.update({
                'uas_tahfidz_count': len(set(x.uas_tahfidz_line.ids)),
            })

    @api.depends('buku_rapot_count')
    def _get_buku_rapot(self):
        for x in self:
            x.update({
                'buku_rapot_count': len(set(x.buku_rapot_line.ids)),
            })

    @api.multi
    def action_view_lp_tahfidz(self):
        lp_tahfidz_ids = self.mapped('lp_tahfidz_line')
        action = self.env.ref('aa_kurikulum.action_portal_lesson_plan').read()[0]
        if len(lp_tahfidz_ids) > 1:
            action['domain'] = [('id', 'in', lp_tahfidz_ids.ids)]
        elif len(lp_tahfidz_ids) == 1:
            form_view = [(self.env.ref('aa_kurikulum.lesson_plan_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = lp_tahfidz_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_view_kbm_tahfidz(self):
        kbm_tahfidz_ids = self.mapped('kbm_tahfidz_line')
        action = self.env.ref('aa_kurikulum.action_portal_kbm_tahfidz').read()[0]
        if len(kbm_tahfidz_ids) > 1:
            action['domain'] = [('id', 'in', kbm_tahfidz_ids.ids)]
        elif len(kbm_tahfidz_ids) == 1:
            form_view = [(self.env.ref('aa_kurikulum.kbm_tahfidz_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = kbm_tahfidz_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_view_mohon_ukj_tahfidz(self):
        mohon_tahfidz_ids = self.mapped('mohon_ukj_tahfidz_line')
        action = self.env.ref('aa_kurikulum.action_portal_permohonan_ukj').read()[0]
        if len(mohon_tahfidz_ids) > 1:
            action['domain'] = [('id', 'in', mohon_tahfidz_ids.ids)]
        elif len(mohon_tahfidz_ids) == 1:
            form_view = [(self.env.ref('aa_kurikulum.permohonan_ukj_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = mohon_tahfidz_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_view_ukj_tahfidz(self):
        ukj_tahfidz_ids = self.mapped('ukj_tahfidz_line')
        action = self.env.ref('aa_kurikulum.action_portal_ukj_tahfidz').read()[0]
        if len(ukj_tahfidz_ids) > 1:
            action['domain'] = [('id', 'in', ukj_tahfidz_ids.ids)]
        elif len(ukj_tahfidz_ids) == 1:
            form_view = [(self.env.ref('aa_kurikulum.ujian_kenaikan_juz_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = ukj_tahfidz_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_view_uas_tahfidz(self):
        uas_tahfidz_ids = self.mapped('uas_tahfidz_line')
        action = self.env.ref('aa_kurikulum.action_portal_uas_tahfidz').read()[0]
        if len(uas_tahfidz_ids) > 1:
            action['domain'] = [('id', 'in', uas_tahfidz_ids.ids)]
        elif len(uas_tahfidz_ids) == 1:
            form_view = [(self.env.ref('aa_kurikulum.uas_tahfidz_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = uas_tahfidz_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_view_buku_rapot(self):
        buku_rapot_ids = self.mapped('buku_rapot_line')
        action = self.env.ref('aa_kurikulum.action_portal_buku_rapot').read()[0]
        if len(buku_rapot_ids) > 1:
            action['domain'] = [('id', 'in', buku_rapot_ids.ids)]
        elif len(buku_rapot_ids) == 1:
            form_view = [(self.env.ref('aa_kurikulum.view_buku_rapot_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = buku_rapot_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    lp_tahfidz_count = fields.Integer(string='LP Tahfidz Count', compute='_get_lp_tahfidz')
    kbm_tahfidz_count = fields.Integer(string='KBM Tahfidz Count', compute='_get_kbm_tahfidz')
    mohon_ukj_tahfidz_count = fields.Integer(string='Permohonan UKJ Count', compute='_get_mohon_ukj_tahfidz')
    ukj_tahfidz_count = fields.Integer(string='UKJ Count', compute='_get_ukj_tahfidz')
    uas_tahfidz_count = fields.Integer(string='UAS Count', compute='_get_uas_tahfidz')

    buku_rapot_count = fields.Integer(string='Rapot Count', compute='_get_buku_rapot')

    lp_tahfidz_line = fields.One2many('lesson.plan', 'siswa_id', string='Lesson Plan Tahfidz', readonly=True)
    kbm_tahfidz_line = fields.One2many('kbm.tahfidz', 'siswa_id', string='KBM Tahfidz', readonly=True)
    mohon_ukj_tahfidz_line = fields.One2many('permohonan.ukj', 'siswa_id', string='Permohonan UKJ', readonly=True)
    ukj_tahfidz_line = fields.One2many('ujian.kenaikan.juz', 'siswa_id', string='UKJ Tahfidz', readonly=True)
    uas_tahfidz_line = fields.One2many('tahfidz.akhir.semester', 'siswa_id', string='UAS Tahfidz', readonly=True)

    buku_rapot_line = fields.One2many('buku.rapot', 'siswa_id', string='Buku Rapot', readonly=True)



# class Menu_Ziyadah(models.Model):
#     _name = 'menu.ziyadah'
#     _description = 'Menu Ziyadah'
    
    
    
#     guru_id = fields.Many2one('hr.employee', string='Nama Halaqah')
#     siswa_id = fields.Many2one('res.partner', string='Nama Santri', domain="[('student', '=', True)]", required=True)
#     jenjang = fields.Selection('Jenjang', related='siswa_id.jenjang')
#     nisn = fields.Char('NISN', related='siswa_id.nisn')
    
#     awal_juz = fields.Char('Awal Juz')
#     awal_pj = fields.Char('Awal PJ')
#     akhir_pj = fields.Char('Akhir PJ')
#     akhir_juz = fields.Char('Akhir Juz')
    
#     total_pj = fields.Char(string='Total PJ')
#     total_pj = fields.Char(compute='_compute_total_pj', string='Total PJ')
#     keterangan = fields.Text('Keterangan')
    
    # laporan_ziyadah_id = fields.Many2one('laporan.bulanan', string='laporan')
    
    # @api.model
    # def create(self, vals):
    #     record = super(Menu_Ziyadah, self).create(vals)
    #     self._update_partner_ziyadah_id(record.siswa_id.id, record.id)
    #     return record

    # def write(self, vals):
    #     res = super(Menu_Ziyadah, self).write(vals)
    #     for record in self:
    #         self._update_partner_ziyadah_id(record.siswa_id.id, record.id)
    #     return res

    # def _update_partner_ziyadah_id(self, partner_id, ziyadah_id):
    #     partner = self.env['res.partner'].browse(partner_id)
    #     if partner:
    #         partner.ziyadah_id = ziyadah_id
    
    # def _domain_siswa_id(self):
    #     used_efakturs = self.env['menu.ziyadah'].search([('siswa_id', '!=', False)])
    #     used_efaktur_ids = used_efakturs.mapped('siswa_id.id')
    #     return [('id', 'not in', used_efaktur_ids)]

    # siswa_id = fields.Many2one('res.partner', string='Nama Santri', domain=_domain_siswa_id)

    
    
    # @api.constrains('siswa_id')
    # def _check_unique_siswa_id(self):
    #     for record in self:
    #         if record.siswa_id:
    #             existing_records = self.env['menu.ziyadah'].search([('siswa_id', '=', record.siswa_id.id)])
    #             if existing_records and len(existing_records) > 1:
    #                 existing_siswa_names = ', '.join(existing_records.mapped('siswa_id.name'))
    #                 raise ValidationError('Siswa {} sudah dipilih. Pilih siswa yang berbeda'.format(existing_siswa_names))
                
                
    # @api.constrains('siswa_id')
    # def _check_unique_siswa_id(self):
    #     for record in self:
    #         if record.siswa_id:
    #             existing_records = self.search([('siswa_id', '=', record.siswa_id.id)])
    #             if existing_records.exists() and len(existing_records) > 1:
    #                 existing_siswa_names = ', '.join(existing_records.mapped('siswa_id.name'))
    #                 raise ValidationError('Siswa {} sudah dipilih. Pilih siswa yang berbeda.'.format(existing_siswa_names))
    
    
    # @api.multi
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         name = "Menu Ziyadah - {}".format(record.siswa_id.name)
    #         # name = "Menu Ziyadah"
    #         result.append((record.id, name))
    #     return result
   
    
    # @api.depends('awal_pj','akhir_pj')
    # def _compute_total_pj(self):
    #     for pj in self:
    #         pj.total_pj = pj.awal_pj + pj.akhir_pj
    
class Menu_Deresan(models.Model):
    _name = 'menu.deresan'
    _description = 'Menu Deresan'
    
    
    
    guru_id = fields.Many2one('res.users', 'Nama Halaqah', readonly=True, required=True, default=lambda self: self.env.user)
    siswa_id = fields.Many2one('res.partner', string='Nama Santri', domain="[('student', '=', True)]", required=True)
    jenjang = fields.Selection('Jenjang', related='siswa_id.jenjang')
    tanggal = fields.Date('Tanggal', default=fields.Date.context_today)
    nisq = fields.Char('NISQ', related='siswa_id.nis')
    
    awal_juz = fields.Char('Awal Juz')
    awal_pj = fields.Char('Awal PJ')
    akhir_pj = fields.Char('Akhir PJ')
    akhir_juz = fields.Char('Akhir Juz')
    
    total_pj = fields.Char(string='Total PJ')
    # total_pj = fields.Char(compute='_compute_total_pj', string='Total PJ')
    keterangan = fields.Text('Keterangan')

    awal_a_juz = fields.Char('Awal Juz')
    awal_a_pj = fields.Char('Awal PJ')
    akhir_a_pj = fields.Char('Akhir PJ')
    akhir_a_juz = fields.Char('Akhir Juz')
    total_a_pj = fields.Char( string='Total PJ')
    # total_a_pj = fields.Char(compute='_compute_total_a_pj', string='Total PJ')
    keterangan_a = fields.Text('Keterangan')
    
    awal_b_juz = fields.Char('Awal Juz')
    awal_b_pj = fields.Char('Awal PJ')  
    akhir_b_pj = fields.Char('Akhir PJ')
    akhir_b_juz = fields.Char('Akhir Juz')
    total_b_pj = fields.Char( string='Total PJ')
    total_deresan = fields.Char(string='Total Deresan A dan B')
    # total_b_pj = fields.Char(compute='_compute_total_b_pj', string='Total PJ')
    # total_deresan = fields.Char(compute='_compute_total_deresan', string='Total Deresan A dan B')
    keterangan_b = fields.Text('Keterangan')
    laporan_deresan_id = fields.Many2one('laporan.bulanan', string='laporan')

    juz = fields.Char('Juz')
    pojok = fields.Char('Pojok')

    awal_m_juz = fields.Char('Awal Juz')
    awal_m_pj = fields.Char('Awal PJ')
    akhir_m_pj = fields.Char('Akhir PJ')
    akhir_m_juz = fields.Char('Akhir Juz')
    
    total_m_pj = fields.Char(string='Total PJ')
    # total_m_pj = fields.Char(compute='_compute_total_pjm', string='Total PJ')
    keterangan_m = fields.Text('Keterangan')
    
    tidak_setor = fields.Char('Tidak Setor')
    ijin = fields.Char('Ijin')
    alpha = fields.Char('Alpha')
    
    @api.model
    def create(self, vals):
        record = super(Menu_Deresan, self).create(vals)
        self._update_partner_deresan_id(record.siswa_id.id, record.id)
        return record

    def write(self, vals):
        res = super(Menu_Deresan, self).write(vals)
        for record in self:
            self._update_partner_deresan_id(record.siswa_id.id, record.id)
        return res

    def _update_partner_deresan_id(self, partner_id, deresan_id):
        partner = self.env['res.partner'].browse(partner_id)
        if partner:
            partner.deresan_id = deresan_id
            
    def name_get(self):
        result = []
        for record in self:
            name = "Menu Deresan - {} - {}".format(record.siswa_id.name, record.tanggal)
            result.append((record.id, name))
        return result
    
    # @api.depends('awal_m_pj','akhir_m_pj')
    # def _compute_total_pjm(self):
    #     for pjm in self:
    #         pjm.total_pj = pjm.awal_m_pj + pjm.akhir_m_pj

    
    # @api.constrains('siswa_id')
    # def _check_unique_siswa_id(self):
    #     for record in self:
    #         if record.siswa_id:
    #             existing_records = self.env['menu.deresan'].search([('siswa_id', '=', record.siswa_id.id)])
    #             if existing_records and len(existing_records) > 1:
    #                 existing_siswa_names = ', '.join(existing_records.mapped('siswa_id.name'))
    #                 raise ValidationError('Siswa {} sudah dipilih. Pilih siswa yang berbeda.'.format(existing_siswa_names))
                
    # @api.constrains('siswa_id')
    # def _check_unique_siswa_id(self):
    #     for record in self:
    #         if record.siswa_id:
    #             existing_records = self.search([('siswa_id', '=', record.siswa_id.id)])
    #             if existing_records.exists() and len(existing_records) > 1:
    #                 existing_siswa_names = ', '.join(existing_records.mapped('siswa_id.name'))
    #                 raise ValidationError('Siswa {} sudah dipilih. Pilih siswa yang berbeda.'.format(existing_siswa_names))
    
    # ZIYADAH

    # @api.multi
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         name = "Menu Ziyadah - {}".format(record.siswa_id.name)
    #         result.append((record.id, name))
    #     return result
   
    
    # @api.depends('awal_pj','akhir_pj')
    # def _compute_total_pj(self):
    #     for pj in self:
    #         pj.total_pj = pj.awal_pj + pj.akhir_pj
            


    # #DERESAN

    # @api.multi
    # def name_get(self):
    #     result = []
    #     for o in self:
    #         # name = "Menu Deresan"
    #         name = "Menu Deresan - {}".format(o.siswa_id.name)
    #         result.append((o.id, name))
    #     return result
    
    # @api.depends('total_a_pj','total_b_pj')
    # def _compute_total_deresan(self):
    #     for rec in self:
    #         rec.total_deresan = rec.total_a_pj + rec.total_b_pj
    
    # @api.depends('awal_a_pj','akhir_a_pj')
    # def _compute_total_a_pj(self):
    #     for pj in self:
    #         pj.total_a_pj = pj.awal_a_pj + pj.akhir_a_pj
    
    # @api.depends('awal_b_pj','akhir_b_pj')
    # def _compute_total_b_pj(self):
    #     for pj in self:
    #         pj.total_b_pj = pj.awal_b_pj + pj.akhir_b_pj


        #MUJAWWADAH
    # @api.multi
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         name = "Menu Mujawwadah - {}".format(record.siswa_id.name)
    #         result.append((record.id, name))
    #     return result
   
    
    # @api.depends('awal_m_pj','akhir_m_pj')
    # def _compute_total_m_pj(self):
    #     for pj_m in self:
    #         pj_m.total_pjm = pj_m.awal_m_pj + pj_m.akhir_m_pj
            

class Menu_KBM(models.Model):
    _name = 'menu.kbm'
    _description = 'Menu KBM'
    
    guru_id = fields.Many2one('hr.employee', string='Nama Halaqah')
    siswa_id = fields.Many2one('res.partner', string='Nama Santri', domain="[('student', '=', True)]", required=True)
    jenjang = fields.Selection('Jenjang', related='siswa_id.jenjang')
    tanggaljam = fields.Datetime(string='Tanggal dan Jam', required=True, readonly=True, default=lambda self: fields.Datetime.now())
    
    
    status_a = fields.Selection([
         ('Izin','Izin'),
        ('Tidak Setor', 'Tidak Setor'),
        ('Alpha', 'Alpha'),
        ('Tugas Lembaga', 'Tugas Lembaga'),
    ], string='Status')
    count_sakit_a = fields.Char('Sakit')
    count_izin_a = fields.Char('Izin')
    count_alpha_a = fields.Char('Alpa')
    count_tugas_a = fields.Char('Tugas Lembaga')
    
    juz_z = fields.Char('Juz')
    pojok_z = fields.Char('Pojok')
    keterangan_z = fields.Text('Keterangan')
    
    awal_juz_ma = fields.Char('Awal Juz')
    awal_pj_ma = fields.Char('Awal PJ')
    akhir_pj_ma = fields.Char('Akhir PJ')
    akhir_juz_ma = fields.Char('Akhir Juz')
    
    total_pj_ma = fields.Char(string='Total Setor')
    # total_pj_ma = fields.Char(compute='_compute_total_pjma', string='Total PJ')
    keterangan_ma = fields.Text('Keterangan')
    
    
    
    status_b = fields.Selection([
         ('Izin','Izin'),
        ('Tidak Setor', 'Tidak Setor'),
        ('Alpha', 'Alpha'),
        ('Tugas Lembaga', 'Tugas Lembaga'),
    ], string='Status')
    count_sakit_b = fields.Char('Sakit')
    count_izin_b = fields.Char('Izin')
    count_alpha_b = fields.Char('Alpa')
    count_tugas_b = fields.Char('Tugas Lembaga')
    
    
    awal_juz_db = fields.Char('Awal Juz')
    awal_pj_db = fields.Char('Awal PJ')
    akhir_pj_db = fields.Char('Akhir PJ')
    akhir_juz_db = fields.Char('Akhir Juz')
    
    total_pj_db = fields.Char(string='Total Setor')
    # total_pj_ma = fields.Char(compute='_compute_total_pjma', string='Total PJ')
    keterangan_db = fields.Text('Keterangan')
    
    juz_ma = fields.Char('Juz')
    pojok_ma = fields.Char('Pojok')
    keterangan_mmm = fields.Text('Keterangan')
    
    total_pj_z = fields.Char(string='Total Murojaah + Ziyadah')
    
    status_c = fields.Selection([
         ('Izin','Izin'),
        ('Tidak Setor', 'Tidak Setor'),
        ('Alpha', 'Alpha'),
        ('Tugas Lembaga', 'Tugas Lembaga'),
    ], string='Status')
    count_sakit_c = fields.Char('Sakit')
    count_izin_c = fields.Char('Izin')
    count_alpha_c = fields.Char('Alpa')
    count_tugas_c = fields.Char('Tugas Lembaga')
    
    
    def name_get(self):
        result = []
        for record in self:
            name = "Menu KBM - {} - {}".format(record.siswa_id.name, record.tanggaljam)
            result.append((record.id, name))
        return result
    # @api.depends('awal_pj_ma','akhir_pj_ma')
    # def _compute_total_pjma(self):
    #     for pjma in self:
    #         pjma.total_pj_ma = pjma.awal_pj_ma + pjma.akhir_pj_ma