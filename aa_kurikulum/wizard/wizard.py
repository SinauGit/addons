import time
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError



jenis_kegiatan = [
    ('Jeda_Semester', 'Jeda Semester'),
    ('Tidak_Masuk_Sekolah', 'Tidak Masuk Sekolah'),
]


class generate_kbm(models.TransientModel):
    _name = "generate.kbm"

    @api.model
    def _penugasan_guru(self):
        domain = [('state', '=', 'In_Progress'), ('guru_id.user_id', '=', self.env.user.id)]
        return self.env['penugasan.guru'].search(domain, limit=1)

    user_id = fields.Many2one('res.users', string='User', readonly=True, default=lambda self: self.env.user)
    penugasan_guru_id = fields.Many2one('penugasan.guru', 'Guru Halaqah', readonly=True, default=lambda self: self._penugasan_guru())
    kalender_id = fields.Many2one('kalender.akademik', 'Pekan KBM', required=True, domain=[('state', '=', 'In_Progress')])
    kegiatan = fields.Selection(jenis_kegiatan, string='Kegiatan', required=True)
    notes = fields.Char(string='Catatan Guru', required=True)

    @api.multi
    def create_kbm(self):
        for o in self:
            if not o.penugasan_guru_id:
                raise UserError(("Penugasan Guru tidak tersedia !"))

            obj_kbm_tahfidz = self.env['kbm.tahfidz']

            for x in o.penugasan_guru_id.halaqah_line:
                kbm_id = obj_kbm_tahfidz.create({
                        'user_id': o.user_id.id,
                        'halaqah_id': x.id,
                        'kalender_id': o.kalender_id.id,
                        'siswa_id': x.siswa_id.id,
                        'kegiatan': o.kegiatan,
                        'notes': o.notes,
                })
                kbm_id.kbm_open()
                kbm_id.kbm_done()

        return True




class Employee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def create_user(self):
        user_id = self.env['res.users'].create({
                            'name': self.name,
                            'login': self.work_email,
                            'password': 'sdcq',
                            'company_id': self.env.ref('base.main_company').id,
                            'groups_id': [(6, 0, [
                                                    self.env.ref('base_sekolah.group_sekolah_admin').id,
                                                    self.env.ref('aa_kurikulum.group_kurikulum_admin').id,
                                                    self.env.ref('aa_kurikulum.group_tahfidz_admin').id,
                                                    self.env.ref('base.group_user').id
                            ])]
                            })
        self.address_home_id = user_id.partner_id.id
        self.user_id = user_id




# class pergantian_guru_lpkbm(models.TransientModel):
#     _name = "pergantian.guru.lpkbm"

#     guru_sebelum_id = fields.Many2one('penugasan.guru', 'Penugasan Sebelumnya', domain=[('state', '=', 'In_Progress')])
#     guru_sesudah_id = fields.Many2one('penugasan.guru', 'Penugasan Penggantinya', domain=[('state', '=', 'In_Progress')])
#     absen_ids = fields.Many2many('absen.penilaian', 'absen_rel', 'penilaian_id', 'absen_id', 'Penilaian Absensi', domain="[('fiscalyear_id', '=', fiscalyear_id), ('class_id', '=', class_id), ('subject_id', '=', subject_id) ('semester', '=', semester)]")
    
    
#     @api.multi
#     def ganti_guru(self):
#         for o in self:
#             if not o.penugasan_guru_id:
#                 raise UserError(("Penugasan Guru tidak tersedia !"))

#             obj_kbm_tahfidz = self.env['kbm.tahfidz']

#             for x in o.penugasan_guru_id.halaqah_line:
#                 kbm_id = obj_kbm_tahfidz.create({
#                         'user_id': o.user_id.id,
#                         'halaqah_id': x.id,
#                         'kalender_id': o.kalender_id.id,
#                         'siswa_id': x.siswa_id.id,
#                         'kegiatan': o.kegiatan,
#                         'notes': o.notes,
#                 })
#                 kbm_id.kbm_open()
#                 kbm_id.kbm_done()

#         return True


