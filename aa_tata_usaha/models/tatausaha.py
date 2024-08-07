from datetime import datetime
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, RedirectWarning, ValidationError

LEMBAGA = [
    # ('KB', 'KB'), ('TK', 'TK'), ('SD', 'SD'), 
    ('SMP', 'SMP'), ('SMA', 'SMA')
    ]

class account_fiscalyear(models.Model):
    _inherit = 'account.fiscalyear'

    harga_komponen = fields.One2many('fiscalyear.harga', 'fiscalyear_id', 'Komponen Price')


class fiscalyear_harga(models.Model):
    _name = "fiscalyear.harga"

    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', required=True, ondelete='cascade')
    name = fields.Many2one('komponen.usaha', 'Komponen', required=True)
    lembaga = fields.Selection(LEMBAGA, string='Lembaga', required=True)
    price_unit = fields.Float('Harga', digits=dp.get_precision('Product Price'))


class komponen_usaha(models.Model):
    _name = "komponen.usaha"

    name = fields.Char('Nama', required=True)
    tujuan = fields.Selection((('yayasan','Yayasan'), ('sekolah','Sekolah')), 'Tujuan', required=True)
    cicil = fields.Selection((('credit', 'Credit'), ('cash','Cash')), 'Payment', required=True, default='cash')
    catering = fields.Boolean('Catering')
    jemputan = fields.Boolean('Jemputan')
    active = fields.Boolean('Active', default=True)
    

class res_partner(models.Model):
    _inherit = 'res.partner'

    bebasbiaya = fields.Boolean('Bebas Biaya')
    harga_komponen = fields.One2many('res.partner.harga', 'partner_id', 'Harga Khusus')


class res_partner_harga(models.Model):
    _name = "res.partner.harga"

    partner_id = fields.Many2one('res.partner', 'Partner', required=True, ondelete='cascade', domain=[('student', '=', True)])
    name = fields.Many2one('komponen.usaha', 'Komponen', required=True)
    disc_amount = fields.Integer('Disc Amount')
    disc_persen = fields.Integer('Disc Percent')
    notes = fields.Char('Keterangan')


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends('invoice_line_ids')
    def _add_line(self):
        self.info_line = ', '.join([line.name for line in self.invoice_line_ids])

    student = fields.Boolean('Siswa')
    cicil = fields.Selection((('credit', 'Credit'), ('cash','Hard Cash')), 'Pembayaran', default='cash')
    orangtua_id = fields.Many2one('res.partner', 'Orang Tua', readonly=True, states={'draft': [('readonly', False)]})
    class_id = fields.Many2one('master.kelas', 'Ruang Kelas', readonly=True, states={'draft': [('readonly', False)]})
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', readonly=True, states={'draft': [('readonly', False)]})
    komponen_id = fields.Many2one('komponen.usaha', 'Komponen', readonly=True, states={'draft': [('readonly', False)]})
    period_id = fields.Many2one('account.period', string='Force Period', copy=False, readonly=True, states={'draft': [('readonly', False)]})

    info_line = fields.Char(compute='_add_line', string='Invoice Line')

    _sql_constraints = [('invoice_uniq', 'unique(komponen_id, partner_id, period_id)', 'Invoice sudah pernah dibuat !')]

    @api.onchange('orangtua_id', 'partner_id', 'class_id', 'fiscalyear_id')
    def onchange_orangtua_id(self):
        if self.partner_id:
            self.update({'class_id': self.class_id.id, 'orangtua_id': self.partner_id.orangtua_id.id, 'fiscalyear_id': self.partner_id.fiscalyear_id.id})
        else:
            self.update({'class_id': False, 'orangtua_id': False, 'fiscalyear_id': False})

    @api.onchange('komponen_id')
    def onchange_komponen_id(self):
        if self.komponen_id:
            product = []; harga = {}
            for o in self.partner_id.fiscalyear_id.harga_komponen:
                harga[o.name.id] = o.price_unit

            price = 0
            i = self.komponen_id.id
            if harga.has_key(i.id):
                price = harga[i.id]
            product.append({
                            'name': i.partner_ref,
                            'uos_id': i.uom_id.id,
                            'price_unit': price,
                            'quantity': 1,
                            'account_id': i.categ_id.property_account_income_categ_id.id
            })

            self.update({'invoice_line_ids': product, 'cicil': self.komponen_id.cicil})


class kehadiran_siswa(models.Model):
    _name = "kehadiran.siswa"

    name = fields.Integer('Hari', required=True, default=1)
    tanggal = fields.Date('Tanggal', required=True, default=fields.Date.context_today)
    siswa_id = fields.Many2one('res.partner', "Siswa", required=True, domain=[('student', '=', True)],ondelete='cascade')
    catering = fields.Boolean("Catering", default=1)
    jemputan = fields.Boolean("Jemputan", default=1)

    @api.multi
    def _get_number_of_days(self, date_from, date_to):
        from_dt = datetime.strptime(date_from, "%Y-%m-%d")
        to_dt = datetime.strptime(date_to, "%Y-%m-%d")
        timedelta = to_dt - from_dt
        diff_day = timedelta.days
        return diff_day

    @api.onchange('date_from', 'date_to')
    def onchange_date(self):
        if (self.date_from and self.date_to) and (self.date_from > self.date_to):
            self.update({'name':1, 'date_from': time.strftime('%Y-%m-%d'), 'date_to': time.strftime('%Y-%m-%d')})

        result = {'value': {'name': 0}}
        if (self.date_to and self.date_from) and (self.date_from <= self.date_to):
            diff_day = self._get_number_of_days(self.date_from, self.date_to)
            result['value']['name'] = diff_day+1 # round(math.floor(diff_day))+1
        return result


class manifest_pembayaran(models.Model):
    _name = "manifest.pembayaran"

    name = fields.Char('Reference', readonly=True, default='/')
    user_id = fields.Many2one('res.users', 'Operator', readonly=True, required=True, default=lambda self: self.env.user, copy=False)
    date = fields.Date('Tanggal', readonly=True, required=True, states={'draft': [('readonly', False)]}, default=fields.Date.context_today)
    siswa_id = fields.Many2one('res.partner', 'Siswa', domain=[('student', '=', True)], readonly=True, states={'draft': [('readonly', False)]})
    orangtua_id = fields.Many2one('res.partner', 'Orang Tua', domain=[('parent', '=', True)], readonly=True, states={'draft': [('readonly', False)]})
    tagihan_ids = fields.Many2many('account.invoice', 'tagihan_rel', 'manifest_id', 'tagihan_id', 'Invoice',
                                   domain=[('type', '=', 'out_invoice')], readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection(compute='compute_state', selection=[('draft', 'Draft'), ('paid', 'Paid')], string='Status', default='draft', store=True)
    currency_id = fields.Many2one("res.currency", string="Currency", compute='_compute_currency_id')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('manifest.pembayaran') or '/'
        result = super(manifest_pembayaran, self).create(vals)
        return result

    @api.multi
    def unlink(self):
        for o in self:
            if o.state == 'paid':
                raise UserError(('Manifest pembayaran tidak bisa dihapus pada status PAID !'))
        return super(manifest_pembayaran, self).unlink()

    @api.onchange('orangtua_id', 'siswa_id')
    def onchange_orangtua_siswa(self):
        value = {}
        domain_tagihan = [('state', '=', 'open'), ('type', '=', 'out_invoice')]
        if self.siswa_id:
            value = {'orangtua_id': self.siswa_id.orangtua_id.id}
            domain_tagihan.append(('partner_id', '=', self.siswa_id.id))
        if self.orangtua_id:
            # value = {'orangtua_id': self.siswa_id.orangtua_id.id}
            domain_tagihan.append(('orangtua_id', '=', self.orangtua_id.id))
        return {'domain': {'tagihan_ids': domain_tagihan}, 'value': value}

    @api.depends('tagihan_ids.amount_total')
    def _amount_all(self):
        for o in self:
            total = 0
            for i in o.tagihan_ids:
                total += i.amount_total
            o.update({
                'amount_total': total,
            })

    @api.multi
    def _compute_currency_id(self):
        try:
            main_company = self.sudo().env.ref('base.main_company')
        except ValueError:
            main_company = self.env['res.company'].sudo().search([], limit=1, order="id")
        for template in self:
            template.currency_id = main_company.currency_id.id

    @api.depends('tagihan_ids.state')
    def compute_state(self):
        for payment in self:
            if len(set([i.state for i in payment.tagihan_ids if i.state == 'paid'])) == 1:
                payment.state = 'paid'
            else:
                payment.state = 'draft'

    @api.multi
    def proses_pembayaran(self):
        for i in self.tagihan_ids:
            if i.state == 'draft':
                raise UserError(('Invoice status draft harus di validate terlebih dahulu'))
                # i.action_invoice_open()
            elif i.state == 'paid':
                raise UserError(('Invoice yang sudah paid tidak bisa diproses'))

        return {
            'name': _('Manifest Pembayaaran'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.register.payments',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_ids': [x.id for x in self.tagihan_ids],
                'active_model': 'account.invoice',
            }
        }


    @api.multi
    def print_manifest(self):
        return self.env.ref('aa_tata_usaha.action_report_manifest').report_action(self)
