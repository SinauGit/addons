from odoo import api, fields, models

class SuratMasuk(models.Model):
    _name = 'surat.masuk'
    _description = 'Surat Masuk'

    no = fields.Integer(string='No')
    tanggal = fields.Date(string='Tanggal')
    nosurat = fields.Integer(string='Nomor')
    tanggalsurat = fields.Date(string='Tanggal')
    tofrom = fields.Char(string='Dari/Kepada')
    ringkasan = fields.Char(string='Ringkasan')
    keterangan = fields.Char(string='Keterangan')
    file_surat = fields.Binary(string='File Surat')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Dikonfirmasi'),
    ], string='Status', readonly=True, copy=False, index=True, default='draft')

    def action_done(self):
        self.write({'state': 'done'})
        self.create_notification({'message': 'Surat masuk berhasil dikonfirmasi.'})

    def action_draft(self):
        self.write({'state': 'draft'})
        
    @api.model
    def create_notification(self, values):
        message = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': ('Success!'),
                'message': values.get('message', ''),
                'sticky': False,
            }
        }
        return message

class SuratKeluar(models.Model):
    _name = 'surat.keluar'
    _description = 'surat keluar'

    no = fields.Integer(string='No')
    tanggal = fields.Date(string='Tanggal')
    nosurat = fields.Integer(string='Nomor')
    tanggalsurat = fields.Date(string='Tanggal')
    tofrom = fields.Char(string='Dari/Kepada')
    ringkasan = fields.Char(string='Ringkasan')
    keterangan = fields.Char(string='Keterangan')
    file_surat = fields.Binary(string='File Surat')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Dikonfirmasi'),
    ], string='Status', readonly=True, copy=False, index=True, default='draft')

    def action_done(self):
        self.write({'state': 'done'})
        self.create_notification({'message': 'Surat keluar berhasil dikonfirmasi.'})

    def action_draft(self):
        self.write({'state': 'draft'})
        
    @api.model
    def create_notification(self, values):
        message = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': ('Success!'),
                'message': values.get('message', ''),
                'sticky': False,
            }
        }
        return message
    
class DataPenugasan(models.Model):
    _name = 'data.penugasan'
    _description = 'Data Penugasan'

    name = fields.Char(string='Nama')
    jabatan = fields.Char(string='Jabatan')
    niy = fields.Char(string='Niy')
    alamat = fields.Char(string='Alamat')
    tanggal = fields.Date(string='Tanggal')
    jam = fields.Datetime(string='Jam')
    tempat = fields.Char(string='Tempat')

    @api.model
    def create(self, values):
        record = super(DataPenugasan, self).create(values)
        message = "Data Penugasan '{}' berhasil dimasukkan!".format(record.name)
        # Create a new mail.message record
        self.env['mail.message'].create({
            'body': message,
            'model': 'data.penugasan',
            'res_id': record.id,
            'message_type': 'notification',  # Set message type as notification
        })
        return record