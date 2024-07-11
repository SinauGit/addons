# -*- coding: utf-8 -*- hr.employee

from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class SuratKepegawaian(models.Model):
    _name = 'surat.kepegawaian'
    _description = 'Data Surat Kepegawaian'

    no_surat = fields.Char(string='No. Dokumen', default='/')
    nama_surat = fields.Char(string='Nama Surat')
    name = fields.Char(string='Nama Pegawai')
    tanggal_jam = fields.Datetime(string='Tanggal dan Jam Keluar')
    tanggal_masuk = fields.Datetime(string='Tanggal dan Jam Masuk')
    unit = fields.Char(string='Unit')
    # unit = fields.Selection([
    #     ('SMP', 'SMP'),
    #     ('SMA', 'SMA'),
    #     ('SECURITY', 'SECURITY'),
    #     ('PONDOK', 'PONDOK')
    #     ], string='Unit')
    keperluan = fields.Char(string='Keperluan')
    upload = fields.Binary(string='Upload File')
    
    
    
class HrLeave(models.Model):
    _inherit = 'hr.leave'
    _description = 'Hr Leave'
    
    
    
    kepegawaian_id = fields.Many2one('surat.kepegawaian', string='Kepegawaian')
    
    
    
    
    def action_validate(self):
        res = super(HrLeave, self).action_validate()

        for record in self:
            leave = self.env['surat.kepegawaian'].search([('name', '=', record.name)], limit=1)

            if not leave:
                leave_vals = {
                    'nama_surat': record.holiday_status_id.name,
                    'tanggal_jam': record.request_date_from,
                    'unit': record.department_id.complete_name,
                    'name' : record.employee_id.name,
                    'keperluan': record.name
                    # 'upload': record.order_line[0].bom_id.id,  # Pastikan ini sesuai dengan kebutuhan
                }
                leave = self.env['surat.kepegawaian'].create(leave_vals)

            record.kepegawaian_id = leave.id

        return res
