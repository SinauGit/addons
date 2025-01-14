from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv.expression import get_unaccent_wrapper
import logging
_logger = logging.getLogger(__name__)

class ScoreList(models.Model):
    _name = 'score.list'

    # Field Definitions
    name = fields.Char('No. Dokumen', required=True, readonly=True, default='/')
    type = fields.Selection([
        ('Work_Sheet', 'Work Sheet (WS)'),
        ('Daily_Test', 'Daily Test (UH)'),
        ('UTS', 'UTS'),
        ('UAS', 'UAS')
    ], string='Tipe', required=True, default='Daily_Test')
    # fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', required=True,
    #                                default=lambda self: self.env['account.fiscalyear'].search([('name', '=', 'TA. 2024/2025')], limit=1))
    user_id = fields.Many2one('res.users', 'Guru', readonly=True, required=True, default=lambda self: self.env.user)
    class_id = fields.Many2one('master.kelas', 'Rombel')
    # class_id = fields.Many2one('master.kelas', 'Rombel', domain="[('fiscalyear_id', '=', fiscalyear_id)]")
    # lembaga = fields.Selection(related='class_id.lembaga', store=True, string='Jenjang')
    subject_id = fields.Many2one('mata.pelajaran', string='Mata Pelajaran', required=True)
    # subject_id = fields.Many2one('mata.pelajaran', string='Mata Pelajaran', domain="[('lembaga', '=', lembaga)]", required=True)
    date1 = fields.Date('Tanggal U1')
    date2 = fields.Date('Tanggal U2')
    date3 = fields.Date('Tanggal U3')
    date4 = fields.Date('Tanggal U4')
    date5 = fields.Date('Tanggal U5')
    score_line = fields.One2many('score.line', 'score_id', 'Tabel Nilai', store=True)
    uts_line = fields.One2many('uts.line', 'score_id', 'Nilai UTS', store=True)
    uas_line = fields.One2many('uas.line', 'score_id', 'Nilai UAS', store=True)
    semester = fields.Selection([
        ('Gasal', 'Gasal'),
        ('Genap', 'Genap')
    ], string='Semester', required=True, default='Gasal')

    _sql_constraints = [('subject_uniq', 'unique(subject_id, type, semester, class_id)', 'Data harus unik !')]
        # _sql_constraints = [('subject_uniq', 'unique(subject_id, type, semester, class_id, fiscalyear_id)', 'Data harus unik !')]

    @api.model
    def create(self, vals):
        if 'type' not in vals:
            raise ValidationError(_('Tipe harus diisi.'))
        if vals['type'] == 'Work_Sheet':
            vals['name'] = self.env['ir.sequence'].next_by_code('score.list.ws')
        elif vals['type'] == 'Daily_Test':
            vals['name'] = self.env['ir.sequence'].next_by_code('score.list.uh')
        elif vals['type'] == 'UTS':
            vals['name'] = self.env['ir.sequence'].next_by_code('score.list.uts')
        elif vals['type'] == 'UAS':
            vals['name'] = self.env['ir.sequence'].next_by_code('score.list.uas')

        result = super(ScoreList, self).create(vals)
        return result

    @api.onchange('class_id')
    def onchange_class_id(self):
        if self.class_id:
            _logger.info('res_line: %s', self.class_id.res_line)

            # Hapus data siswa yang ada terlebih dahulu
            self.score_line = [(5, 0, 0)]
            self.uts_line = [(5, 0, 0)]
            self.uas_line = [(5, 0, 0)]

            # Gunakan res_line sebagai sumber data siswa
            siswa_field = self.class_id.res_line

            if not siswa_field:
                raise UserError(_('Tidak ada siswa terdaftar di kelas ini.'))

            nilai = [{'name': x.id} for x in siswa_field]

            _logger.info('Nilai: %s', nilai)

            if self.type == 'UTS':
                self.uts_line = [(0, 0, line) for line in nilai]
            elif self.type == 'UAS':
                self.uas_line = [(0, 0, line) for line in nilai]
            else:
                self.score_line = [(0, 0, line) for line in nilai]

    @api.depends('score_line.u1', 'score_line.u2', 'score_line.u3', 'score_line.u4', 'score_line.u5')
    def compute_score(self):
        for record in self:
            if record.type in ('Work_Sheet', 'Daily_Test'):
                n = 0
                r = record.score_line[0] if record.score_line else None

                if r and r.u1:
                    n += 1
                if r and r.u2:
                    n += 1
                if r and r.u3:
                    n += 1
                if r and r.u4:
                    n += 1
                if r and r.u5:
                    n += 1

                for x in record.score_line:
                    total_sum = x.u1 + x.u2 + x.u3 + x.u4 + x.u5
                    if n > 0:
                        x.sum = total_sum
                        x.avg = total_sum / n


class ScoreLine(models.Model):
    _name = 'score.line'

    score_id = fields.Many2one('score.list', 'Daftar Nilai', required=True, ondelete='cascade')
    name = fields.Many2one('res.partner', 'Siswa', required=True, domain=[('student', '=', True)])
    u1 = fields.Integer('U1')
    u2 = fields.Integer('U2')
    u3 = fields.Integer('U3')
    u4 = fields.Integer('U4')
    u5 = fields.Integer('U5')
    sum = fields.Integer('Total', readonly=True)
    avg = fields.Integer('Rata-Rata', readonly=True)


class UtsLine(models.Model):
    _name = 'uts.line'

    score_id = fields.Many2one('score.list', 'Daftar Nilai', required=True, ondelete='cascade')
    name = fields.Many2one('res.partner', 'Siswa', required=True, domain=[('student', '=', True)])
    nilai = fields.Integer('Nilai')


class UasLine(models.Model):
    _name = 'uas.line'

    score_id = fields.Many2one('score.list', 'Daftar Nilai', required=True, ondelete='cascade')
    name = fields.Many2one('res.partner', 'Siswa', required=True, domain=[('student', '=', True)])
    nilai = fields.Integer('Nilai')





class sholat_performance(models.Model):
    _name = 'sholat.performance'

    name = fields.Char('No. Dokumen', required=True, readonly=True, default='/')
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', required=True)
    class_id = fields.Many2one('master.kelas', 'Rombel', domain="[('fiscalyear_id', '=', fiscalyear_id)]")
    performance_line = fields.One2many('sholat.performance.line', 'performance_id', 'Prestasi Sholat')
    semester = fields.Selection([('Gasal', 'Gasal'), ('Genap', 'Genap')], string='Semester', required=True, default='Gasal')

    _sql_constraints = [('performance_uniq', 'unique(semester, class_id, fiscalyear_id)', 'Data harus unik !')]

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('score.list.ps') or '/'

        result = super(sholat_performance, self).create(vals)
        return result

    @api.onchange('class_id')
    def onchange_class_id(self):
        if self.class_id:

            nilai = []
            for x in self.class_id.res_line:
                nilai.append({'name': x.id, 'u1':100, 'u2':100, 'u3':100, 'u4':100, 'u5':100, 'u6':100, 'u7':100, 'u8':100, 'u9':100, 'u10':100, 'u11':100, 'u12':100, 'u13':100, 'u14':100, 'u15':100, 'u16':100, 'u17':100, 'u18':100, 'u19':100, 'u20':100})

            data = {'performance_line': nilai}
            self.update(data)

    @api.one
    def compute_score(self):
        n = 0
        r = self.performance_line[0]

        if r.u1:
            n += 1
        if r.u2:
            n += 1
        if r.u3:
            n += 1
        if r.u4:
            n += 1
        if r.u5:
            n += 1

        if r.u6:
            n += 1
        if r.u7:
            n += 1
        if r.u8:
            n += 1
        if r.u9:
            n += 1
        if r.u10:
            n += 1

        if r.u11:
            n += 1
        if r.u12:
            n += 1
        if r.u13:
            n += 1
        if r.u14:
            n += 1
        if r.u15:
            n += 1

        if r.u16:
            n += 1
        if r.u17:
            n += 1
        if r.u18:
            n += 1
        if r.u19:
            n += 1
        if r.u20:
            n += 1

        for x in self.performance_line:
            sum = x.u1 + x.u2 + x.u3 + x.u4 + x.u5 + x.u6 + x.u7 + x.u8 + x.u9 + x.u10 + x.u11 + x.u12 + x.u13 + x.u14 + x.u15 + x.u16 + x.u17 + x.u18 + x.u19 + x.u20
            x.write({'sum': sum, 'avg': sum/n})
        return True


class sholat_performance_line(models.Model):
    _name = 'sholat.performance.line'

    performance_id = fields.Many2one('sholat.performance', 'Prestasi Mingguan', required=True, ondelete='cascade')
    name = fields.Many2one('res.partner', 'Siswa', required=True, domain=[('student', '=', True)])
    u1 = fields.Integer('1', default=100)
    u2 = fields.Integer('2', default=100)
    u3 = fields.Integer('3', default=100)
    u4 = fields.Integer('4', default=100)
    u5 = fields.Integer('5', default=100)
    u6 = fields.Integer('6', default=100)
    u7 = fields.Integer('7', default=100)
    u8 = fields.Integer('8', default=100)
    u9 = fields.Integer('9', default=100)
    u10 = fields.Integer('10', default=100)
    u11 = fields.Integer('11', default=100)
    u12 = fields.Integer('12', default=100)
    u13 = fields.Integer('13', default=100)
    u14 = fields.Integer('14', default=100)
    u15 = fields.Integer('15', default=100)
    u16 = fields.Integer('16', default=100)
    u17 = fields.Integer('17', default=100)
    u18 = fields.Integer('18', default=100)
    u19 = fields.Integer('19', default=100)
    u20 = fields.Integer('20', default=100)
    sum = fields.Integer('SUM', readonly=True)
    avg = fields.Integer('AVG', readonly=True)


class absen_penilaian(models.Model):
    _name = 'absen.penilaian'

    name = fields.Date('Tanggal', required=True, default=fields.Date.context_today)
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', required=True)
    class_id = fields.Many2one('master.kelas', 'Rombel', domain="[('fiscalyear_id', '=', fiscalyear_id)]")
    subject_id = fields.Many2one('mata.pelajaran', 'Mata Pelajaran', required=True)
    semester = fields.Selection([('Gasal', 'Gasal'), ('Genap', 'Genap')], string='Semester', required=True, default='Gasal')
    penilaian_line = fields.One2many('penilaian.line', 'penilaian_id', 'Valuation Lines')

    _sql_constraints = [('valuation_uniq', 'unique(semester, subject_id, name, class_id, fiscalyear_id)', 'Data harus unik !')]
    @api.onchange('class_id')
    def onchange_class_id(self):
        if self.class_id:

            nilai = []
            for x in self.class_id.res_line:
                nilai.append({'name': x.id})

            data = {'penilaian_line': nilai}
            self.update(data)


class penilaian_line(models.Model):
    _name = 'penilaian.line'

    penilaian_id = fields.Many2one('absen.penilaian', 'Penilaian Kehadiran', required=True, ondelete='cascade')
    name = fields.Many2one('res.partner', 'Siswa', required=True, domain=[('student', '=', True)])


class summary_book(models.Model):
    _name = 'summary.book'

    name = fields.Char('No. Dokumen', required=True, readonly=True, default='/')
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', required=True)
    user_id = fields.Many2one('res.users', 'Guru', readonly=True, required=True, default=lambda self: self.env.user)
    class_id = fields.Many2one('master.kelas', 'Rombel', domain="[('fiscalyear_id', '=', fiscalyear_id)]")
    subject_id = fields.Many2one('mata.pelajaran', 'Mata Pelajaran', required=True)
    semester = fields.Selection([('Gasal', 'Gasal'), ('Genap', 'Genap')], string='Semester', required=True, default='Gasal')
    summary_line = fields.One2many('summary.line', 'summary_id', 'Ringkasan')
    avg_class = fields.Integer('Rata-Rata Kelas', readonly=True)

    salat_id = fields.Many2one('sholat.performance', 'Prestasi Sholat', domain="[('fiscalyear_id', '=', fiscalyear_id), ('class_id', '=', class_id), ('semester', '=', semester)]")
    sheet_id = fields.Many2one('score.list', 'WS', domain="[('fiscalyear_id', '=', fiscalyear_id), ('class_id', '=', class_id), ('subject_id', '=', subject_id), ('semester', '=', semester), ('type', '=', 'Work_Sheet')]")
    absen_ids = fields.Many2many('absen.penilaian', 'absen_rel', 'penilaian_id', 'absen_id', 'Penilaian Absensi', domain="[('fiscalyear_id', '=', fiscalyear_id), ('class_id', '=', class_id), ('subject_id', '=', subject_id), ('semester', '=', semester)]")
    ulangan_id = fields.Many2one('score.list', 'UH', domain="[('fiscalyear_id', '=', fiscalyear_id), ('class_id', '=', class_id), ('subject_id', '=', subject_id), ('semester', '=', semester), ('type', '=', 'Daily_Test')]")
    uts_id = fields.Many2one('score.list', 'UTS', domain="[('fiscalyear_id', '=', fiscalyear_id), ('class_id', '=', class_id), ('subject_id', '=', subject_id), ('semester', '=', semester), ('type', '=', 'UTS')]")
    uas_id = fields.Many2one('score.list', 'UAS', domain="[('fiscalyear_id', '=', fiscalyear_id), ('class_id', '=', class_id), ('subject_id', '=', subject_id), ('semester', '=', semester), ('type', '=', 'UAS')]")

    _sql_constraints = [('summary_uniq', 'unique(subject_id, semester, class_id, fiscalyear_id)', 'Data harus unik!')]

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('summary.book') or '/'
        result = super(summary_book, self).create(vals)
        return result

    @api.onchange('class_id')
    def onchange_class_id(self):
        if self.class_id:
            nilai = [{'name': x.id} for x in self.class_id.res_line]
            self.summary_line = nilai

    @api.multi
    def compute_score(self):
        obj_sl_line = self.env['score.line']
        obj_sp_line = self.env['sholat.performance.line']
        obj_ap_line = self.env['penilaian.line']
        obj_uts_line = self.env['uts.line']
        obj_uas_line = self.env['uas.line']

        gt = 0
        for x in self.summary_line:
            ws = uh = av = sp = uts = uas = all = 0

            if self.sheet_id:
                wsid = obj_sl_line.search([('score_id', '=', self.sheet_id.id), ('name', '=', x.name.id)], limit=1)
                if wsid:
                    ws = wsid.avg

            if self.ulangan_id:
                uhid = obj_sl_line.search([('score_id', '=', self.ulangan_id.id), ('name', '=', x.name.id)], limit=1)
                if uhid:
                    uh = uhid.avg

            if self.uts_id:
                utsid = obj_uts_line.search([('score_id', '=', self.uts_id.id), ('name', '=', x.name.id)], limit=1)
                if utsid:
                    uts = utsid.nilai

            if self.uas_id:
                uasid = obj_uas_line.search([('score_id', '=', self.uas_id.id), ('name', '=', x.name.id)], limit=1)
                if uasid:
                    uas = uasid.nilai

            if self.absen_ids:
                abn = [i.id for i in self.absen_ids]
                avid = obj_ap_line.search([('penilaian_id', 'in', abn), ('name', '=', x.name.id)], limit=1)
                if avid:
                    av = int(len(avid) / float(len(abn)) * 100)

            if self.salat_id:
                spid = obj_sp_line.search([('performance_id', '=', self.salat_id.id), ('name', '=', x.name.id)], limit=1)
                if spid:
                    sp = spid.avg
                all = (0.05 * ws) + (0.15 * uh) + (0.1 * av) + (0.2 * sp) + (0.2 * uts) + (0.3 * uas)
            else:
                all = (0.05 * ws) + (0.15 * uh) + (0.1 * av) + (0.3 * uts) + (0.4 * uas)

            gt += all
            x.write({'ws': ws, 'uh': uh, 'av': av, 'sp': sp, 'uts': uts, 'uas': uas, 'all': all})

        if len(self.summary_line) > 0:
            self.write({'avg_class': gt / len(self.summary_line)})
        else:
            self.write({'avg_class': 0})



class summary_line(models.Model):
    _name = 'summary.line'

    summary_id = fields.Many2one('summary.book', 'Perhitungan Nilai Raport', required=True, ondelete='cascade')
    name = fields.Many2one('res.partner', 'Siswa', required=True, domain=[('student', '=', True)])
    ws = fields.Integer('AVG WS')
    uh = fields.Integer('AVG UH')
    av = fields.Integer('AVG AV')
    sp = fields.Integer('AVG SP')
    uts = fields.Integer('UTS')
    uas = fields.Integer('UAS')
    all = fields.Integer('AVG ALL')


class buku_rapot(models.Model):
    _name = 'buku.rapot'

    name = fields.Char('No. Dokumen', required=True, readonly=True, default='/')
    siswa_id = fields.Many2one('res.partner', 'Siswa', required=True, domain="[('student', '=', True), ('class_id', '=', class_id)]")
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', required=True,
                                   default=lambda self: self.env['account.fiscalyear'].search([('name', '=', 'TA. 2024/2025')], limit=1))
    class_id = fields.Many2one('master.kelas', 'Rombel', domain="[('fiscalyear_id', '=', fiscalyear_id)]")
    semester = fields.Selection([('Gasal', 'Gasal'), ('Genap', 'Genap')], string='Semester', required=True, default='Gasal')
    avg_class = fields.Integer('Nilai Rata-Rata', readonly=True)
    avg_mulok = fields.Integer('Nilai Rata-Rata Mulok', readonly=True)
    jumlah = fields.Integer('Jumlah Nilai Prestasi', readonly=True)
    peringkat = fields.Integer('Peringkat Kelas', readonly=True)
    rapot_line = fields.One2many('rapot.line', 'rapot_id', 'Daftar Nilai')

    _sql_constraints = [('bukurapot_uniq', 'unique(siswa_id, semester, class_id, fiscalyear_id)', 'Data harus unik !')]
    total = fields.Integer('Total', compute="_compute_total")
    total_line = fields.Integer('Total Line', compute="_compute_total_line")
    rata = fields.Integer('Rata', compute="_compute_rata")
    date = fields.Date('Tanggal Cetak')
    
    @api.model
    def create(self, vals):
        # Generate sequence if name is not provided
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('buku.rapot') or '/'
        # Create the record
        record = super(buku_rapot, self).create(vals)
        # Update the ziyadah_id in res.partner
        self._update_partner_rekap_id(record.siswa_id.id, record.id)
        
        return record
    

    def write(self, vals):
        res = super(buku_rapot, self).write(vals)
        for record in self:
            self._update_partner_rekap_id(record.siswa_id.id, record.id)
        return res

    def _update_partner_rekap_id(self, partner_id, rekap_id):
        partner = self.env['res.partner'].browse(partner_id)
        if partner:
            partner.rekap_id =  rekap_id
    
    
    @api.multi
    def _compute_rata(self):
        for rec in self:
            if rec.total_line != 0:
                rec.rata = rec.total / rec.total_line
            else:
                rec.rata = 0
    
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
    
    @api.multi
    def nilai(self):
        for rec in self:
            for line in rec.rapot_line:
                # Asumsi bahwa ada field mapel_id pada rapot_line yang menghubungkan ke mata.pelajaran
                rekap_lines = self.env['rekap.rapot'].search([
                    ('mapel_id', '=', line.name.id),
                    ('class_id', '=', rec.class_id.id)
                ])
                for rekap_line in rekap_lines:
                    # Asumsi bahwa rekap.rapot memiliki field nilai, kkm, note, dan status
                    rapot_lines = rekap_line.rapot_line.filtered(lambda r: r.siswa_id.id == rec.siswa_id.id)
                    for rapot_line in rapot_lines:
                        line.write({
                            'nilai': rapot_line.nilai,
                            'kkm': rapot_line.kkm,
                            'note': rapot_line.note,
                            'status': rapot_line.status
                        })
        
    @api.multi
    def name_get(self):
        result = []
        for o in self:
            name = "Buku Raport - {} - {}".format(o.siswa_id.name, o.date)
            result.append((o.id, name))
        return result

    @api.multi
    def print_rapot(self):
        return self.env.ref('aa_kurikulum.print_raport_sekolah').report_action(self)

    @api.onchange('siswa_id')
    def onchange_siswa_id(self):
        if self.siswa_id:
            data = {}; mata = []
            data = {'fiscalyear_id': self.siswa_id.fiscalyear_id.id, 'class_id': self.siswa_id.class_id.id}

            val = self.env['mata.pelajaran'].search([('lembaga', '=', self.class_id.lembaga)])
            # val = self.env['mata.pelajaran'].search([('class_id.lembaga', '=', self.class_id)])
            for x in val:
                mata.append({'sequence': x.urut, 'name': x.id})

            data['rapot_line'] = mata
            self.update(data)

    @api.multi
    def compute_score(self):
        obj_sl_line = self.env['summary.line']

        for i in self.rapot_line:
            slid = obj_sl_line.search([('name', '=', self.siswa_id.id), ('summary_id.subject_id', '=', i.name.id), ('summary_id.class_id', '=', self.class_id.id)], limit=1)
            if slid:
                i.write({'kkm': 70, 'nilai': slid.all, 'avg': 75})

        return True


class rapot_line(models.Model):
    _name = 'rapot.line'

    rapot_id = fields.Many2one('buku.rapot', 'Buku Raport', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence')
    name = fields.Many2one('mata.pelajaran', 'Mata Pelajaran', required=True)
    kkm = fields.Integer('KKM')
    nilai = fields.Integer('Nilai')
    avg = fields.Integer('Rata-Rata Kelas')
    note = fields.Char('Catatan Guru')
    rekap_id = fields.Many2one('rekap.rapot', string='Rekap')
    status = fields.Selection([
        ('remidi', 'REMIDI'),
        ('tuntas', 'TUNTAS')
    ], string='Status')  
    
                    
