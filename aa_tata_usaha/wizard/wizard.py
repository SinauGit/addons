from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
import time
from odoo.exceptions import UserError


LEMBAGA = [
    # ('KB', 'KB'), ('TK', 'TK'), ('SD', 'SD'), 
    ('SMP', 'SMP'), ('SMA', 'SMA')]


class bayar_cicil_tagihan(models.TransientModel):
    _name = "bayar.cicil.tagihan"

    name = fields.Float("Nilai", digits=dp.get_precision('Product Price'), required=True)
    invoice_id = fields.Many2one('account.invoice', 'Invoice', required=True, ondelete='CASCADE')

    @api.multi
    def do_cicilan(self):
        obj_invoice = self.env['account.invoice']
        obj_invoice_line = self.env['account.invoice.line']

        cicil = self.name
        inv = self.invoice_id
        lid = inv.invoice_line_ids[0]
        if cicil > lid.price_unit:
            raise UserError(('Perhatian !'), ('Jumlah cicilan lebih besar dari tagihan.'))

        no = self.invoice_id.number
        sisa = lid.price_unit-cicil

        inv.action_invoice_cancel()
        inv.action_invoice_draft()

        inv.write({'user_id': self.env.uid})
        lid.write({'price_unit': cicil, 'discount': 0})

        iid = obj_invoice.create({
            'name': 'Pembayaran Cicilan ' + no,
            'origin': no,
            'type': 'out_invoice',
            'account_id': inv.partner_id.property_account_receivable_id.id,
            'student': True,
            'cicil': 'credit',
            'komponen_id': inv.komponen_id.id,
            'fiscalyear_id': inv.fiscalyear_id.id,
            'orangtua_id': inv.orangtua_id.id,
            'partner_id': inv.partner_id.id,
            'partner_shipping_id': inv.partner_id.id,
            'journal_id': inv.journal_id.id,
            'currency_id': inv.currency_id.id,
            'payment_term_id': inv.payment_term_id.id or False,
            'fiscal_position_id': inv.fiscal_position_id.id or inv.partner_id.property_account_position_id.id,
            'date_invoice': time.strftime("%Y-%m-%d"),
            'company_id': inv.company_id.id,
            'user_id': inv.user_id.id or False
        })


        obj_invoice_line.create({
                'name': lid.name,
                'invoice_id': iid.id,
                'origin': no,
                'account_id': lid.account_id.id,
                'price_unit': sisa,
                'discount': lid.discount,
                'quantity': lid.quantity,
                'uom_id': lid.uom_id.id,
        })

        inv.action_invoice_open()
        iid.action_invoice_open()

        return {'type': 'ir.actions.act_window_close'}


class generate_invoice(models.TransientModel):
    _name = "generate.invoice"

    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', required=True)
    komponen_id = fields.Many2one('komponen.usaha', 'Komponen', required=True)
    period_from = fields.Many2one('account.period', 'Bulan Awal', required=True, domain="[('special', '=', False), ('fiscalyear_id', '=', fiscalyear_id)]")
    period_to = fields.Many2one('account.period', 'Bulan Akhir', required=True, domain="[('special', '=', False), ('fiscalyear_id', '=', fiscalyear_id)]")
    lembaga = fields.Selection(LEMBAGA, string='Lembaga', required=True)
    partner_ids = fields.Many2many('res.partner', 'partner_rel', 'siswa_id', 'partner_id', 'Students', required=True, domain="[('bebasbiaya', '=', False), ('lembaga', '=', lembaga), ('fiscalyear_id', '=', fiscalyear_id)]")
    name = fields.Integer('Harga')
    
    @api.onchange('fiscalyear_id')
    def onchange_fiscalyear_id(self):
        if self.fiscalyear_id:
            self.update({'partner_ids': False, 'lembaga': False, 'komponen_id': False})

    @api.onchange('komponen_id', 'name', 'lembaga')
    def onchange_komponen_id(self):
        if self.komponen_id:
            harga = self.env['fiscalyear.harga'].search([('fiscalyear_id', '=', self.fiscalyear_id.id), ('lembaga', '=', self.lembaga), ('name', '=', self.komponen_id.id)], limit=1)
            if not harga:
                return {
                    'value': {'partner_ids': False, 'komponen_id': False, 'name': 0, 'lembaga': False},
                    'warning': {'title': 'Perhatian', 'message': 'Harga komponen belum di tentukan pada tahun ajaran'}
                }

            self.update({'name': harga.price_unit})

    @api.multi
    def create_invoice(self):
        if self.period_from.id > self.period_to.id:
            raise UserError(("Bulan Awal lebih besar daripada bulan akhir !"))
        elif not self.partner_ids:
            raise UserError(("Siswa belum di pilih !"))

        obj_hadir = self.env['kehadiran.siswa']
        obj_period = self.env['account.period']
        obj_invoice = self.env['account.invoice']
        obj_invoice_line = self.env['account.invoice.line']

        journal_id = obj_invoice.default_get(['journal_id'])['journal_id']
        period_ids = obj_period.search([('id', 'in', [i for i in range (self.period_from.id, self.period_to.id+1)])])

        # raise UserError(("Period %s !" % [i for i in range (self.period_from.id, self.period_to.id+1)]))

        produk = self.env['product.template'].search([], limit=1)

        print ('======================================>', period_ids)

        for period in period_ids:

            print ('#############################>', period.id, period.name)

            for x in self.partner_ids:
                disc_amount = 0; disc_persen = 0
                if x.harga_komponen:
                    disc = self.env['res.partner.harga'].search([('partner_id', '=', x.id), ('name', '=', self.komponen_id.id)])
                    if disc:
                        disc_amount = disc.disc_amount
                        disc_persen = disc.disc_persen

                qty = 1
                if self.komponen_id.catering:
                    hari = obj_hadir.search([('siswa_id', '=', x.id), ('catering', '=', True), ('tanggal', '>=', period.date_start), ('tanggal', '<=', period.date_end)])
                    qty = sum([h.name for h in hari])
                elif self.komponen_id.jemputan:
                    hari = obj_hadir.search([('siswa_id', '=', x.id), ('jemputan', '=', True), ('tanggal', '>=', period.date_start), ('tanggal', '<=', period.date_end)])
                    qty = sum([h.name for h in hari])

                zid = obj_invoice.create({
                        'name': 'Generate Invoice',
                        'type': 'out_invoice',
                        'account_id': x.property_account_receivable_id.id,
                        'student': True,
                        'cicil': self.komponen_id.cicil,
                        'komponen_id': self.komponen_id.id,
                        'fiscalyear_id': self.fiscalyear_id.id,
                        'class_id': x.class_id.id,
                        'orangtua_id': x.orangtua_id.id,
                        'partner_id': x.id,
                        'partner_shipping_id': x.id,
                        'journal_id': journal_id,
                        'currency_id': self.env.user.company_id.currency_id.id,
                        'fiscal_position': x.property_account_position_id.id,
                        'date_invoice': period.date_start,
                        'company_id': self.env.user.company_id.id,
                        'period_id': period.id,
                        'user_id': self.env.uid or False
                    })

                obj_invoice_line.create({
                        'name': self.komponen_id.name,
                        'discount': disc_persen,
                        'discount_amount': disc_amount,
                        'invoice_id': zid.id,
                        'account_id': produk.property_account_income_id.id or produk.categ_id.property_account_income_categ_id.id,
                        'price_unit': self.name,
                        'quantity': qty,
                        # 'uom_id': produk.uom_id.id,
                })

        return True



class laporan_accounting(models.TransientModel):
    _name = "laporan.accounting"

    name = fields.Many2one('res.users', 'Operator')
    date_start = fields.Date('Tanggal Awal', required=True, default=fields.Date.context_today)
    date_stop = fields.Date('Tanggal Akhir', required=True, default=fields.Date.context_today)
    komponen_line = fields.Many2many('komponen.usaha', 'komponen_rel', 'usaha_id', 'komponen_id', 'Komponen')
    grouping = fields.Selection((('komponen','Komponen'), ('kelas','Kelas')), 'Group By', required=True, default='komponen')
    tipe = fields.Selection((('user','Harian @ User'),
                             ('all','Harian All User'),
                             ('yayasan','Harian Yayasan'),
                             ('sekolah','Harian Sekolah'),
                             ('tunggak', 'Tunggakan')), 'Tipe', required=True, default='user')


    @api.multi
    def bulan(self, bul):
        bln = (bul).split('/')
        return bln[0]

    @api.multi
    def eksport_excel(self):
        obj_payment = self.env['account.payment']
        obj_komponen = self.env['komponen.usaha']

        by1 = self.date_start
        by2 = self.date_stop

        komponen = ('invoice_ids.komponen_id', 'not in', [])
        if self.tipe not in ('yayasan', 'sekolah'):
            if self.komponen_line:
                komponen = ('invoice_ids.komponen_id', 'in', [v.id for v in self.komponen_line])

        laporan = 'harian.user'
        payment_ids = obj_payment.search([('create_uid', '=', self.name.id), ('payment_date', '>=', by1), ('payment_date', '<=', by2), ('invoice_ids.state', '=', 'paid'), komponen])

        if self.tipe == 'all':
            laporan = 'harian.all'
            payment_ids = obj_payment.search([('payment_date', '>=', by1), ('payment_date', '<=', by2), ('invoice_ids.state', '=', 'paid'), komponen])

        elif self.tipe == 'yayasan':
            laporan = 'harian.yayasan'
            payment_ids = obj_payment.search([('invoice_ids.komponen_id.tujuan', '=', 'yayasan'), ('payment_date', '>=', by1), ('payment_date', '<=', by2), ('invoice_ids.state', '=', 'paid')])

        elif self.tipe == 'sekolah':
            laporan = 'harian.sekolah'
            payment_ids = obj_payment.search([('invoice_ids.komponen_id.tujuan', '=', 'sekolah'), ('payment_date', '>=', by1), ('payment_date', '<=', by2), ('invoice_ids.state', '=', 'paid')])

        elif self.tipe == 'tunggak':
            laporan = 'laporan.tunggakan'
            payment_ids = obj_payment.search([('payment_date', '>=', by1), ('payment_date', '<=', by2), ('invoice_ids.state', '=', 'open'), komponen])


        lines = []; user = ''; kelompok ={}
        for p in payment_ids:
            user = p.create_uid.name
            for i in p.invoice_ids:
                komponen = i.komponen_id
                kelas = i.partner_id.class_id
                if self.grouping == 'komponen':
                    var = kelas.name
                    kelompok[komponen.id] = {'nama': '', 'total': 0, 'hasil': []}
                elif self.grouping == 'kelas':
                    var = komponen.name
                    kelompok[kelas.id] = {'nama': '', 'total': 0, 'hasil': []}
                lines.append({
                              'kid': komponen.id,
                              'cid': kelas.id,
                              'number': i.number,
                              'komponen': komponen.name,
                              'siswa': i.partner_id.name,
                              'var': var,
                              'kelas': kelas.name,
                              'nis': i.partner_id.nis,
                              'price_subtotal': i.amount_total,
                              'payment_date': p.payment_date,
                              'period': self.bulan(i.period_id.name)
                })

        for l in lines:
            if self.grouping == 'komponen':
                kelompok[l['kid']]['nama'] = l['komponen']
                kelompok[l['kid']]['total'] += l['price_subtotal']
                kelompok[l['kid']]['hasil'].append(l)
            elif self.grouping == 'kelas':
                kelompok[l['cid']]['nama'] = l['kelas']
                kelompok[l['cid']]['total'] += l['price_subtotal']
                kelompok[l['cid']]['hasil'].append(l)

        # print (kelompok)
        #
        # {
        # 2: {
        #     'total': 1000000.0, 'nama': 'SPP', 'hasil': [
        #                                                 {'number': 'INV/2019/0003', 'payment_date': datetime.date(2020, 3, 11), 'nis': '1911203072030', 'price_subtotal': 500000.0, 'komponen': 'SPP', 'kelas': 'KHADIJAH', 'period': '09', 'kid': 2, 'produk': '[002] SPP', 'cid': 2, 'siswa': 'AURA SHIFA NAJWA QOLBI', 'var': 'KHADIJAH'},
        #                                                 {'number': 'INV/2019/0006', 'payment_date': datetime.date(2020, 3, 11), 'nis': '1911203072030', 'price_subtotal': 500000.0, 'komponen': 'SPP', 'kelas': 'KHADIJAH', 'period': '08', 'kid': 2, 'produk': '[002] SPP', 'cid': 2, 'siswa': 'AURA SHIFA NAJWA QOLBI', 'var': 'KHADIJAH'}
        #                                                 ]
        #     }
        # }


        # form = self.read()[0]
        #
        # form['user'] = user
        # datas = {'ids': [form['id']]}
        # datas['model'] = 'laporan.accounting'
        # datas['form'] = form
        # datas['form']['kelompok'] = kelompok
        #
        # return {
        #     'type': 'ir.actions.report.xml',
        #     'report_name': laporan,
        #     'datas': datas,
        # }
