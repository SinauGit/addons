import json
from odoo import http
from odoo.http import request
from datetime import datetime, date
from odoo.exceptions import ValidationError
import psycopg2

class OnlineRegistrationWeb(http.Controller):

    @http.route('/pendaftaran/form',type="http", auth="public", website=True)
    def registration_details(self, **kwargs):
        return request.render('aa_pendaftaran_online.pendaftaran_html_form',{})

    @http.route('/pendaftaran/form/submit',type="http", auth="public", website=True)
    def create_data_crm(self, **kwargs): 
        error = False

        name = kwargs['name']
        street = kwargs['street']
        phone = kwargs['phone']
        mobile = kwargs['mobile']
        email = kwargs['email']
        jenjang = kwargs['jenjang']

        crm = request.env['crm.lead']
        crm_data = {
            'name': name,
            'street': street,
            'phone': phone,
            'mobile': mobile,
            'email_from': email,
            'jenjang': jenjang,
        }
        check_email = self.check_email(email)
        try:
            self.validation_error(check_email)
        except ValidationError:
            error = {}
            error['error_message'] = ["Anda sudah pernah mendaftarkan email %s ke website ini" % (email)]
        
        if not check_email:            
            crm.sudo().create(crm_data)
        
        message_body = "<h1>Terima Kasih</h1>"
        message_body += "<h1>Data Anda telah kami simpan. </h1>"
        message_body += "<h1>Email : <b>%s</b></h1>" % (email)
        message_body += "<h1>Password : <b>saci</b></h1>"
        message_body += "<h1>Silakan lakukan <a href='https://sekolahalamcitrainsani.sch.id/web/login'>login</a> dengan email yang Anda daftarkan untuk melaksanakan pengisian formulir dan tahapan selanjutnya.</h1>"
                
        create_values = {
                'body_html': message_body,
                'subject': "Terimakasih Telah Mendaftar # Sekolah Alam Citra Insani",
                'email_to': email,                
            }

        mail = request.env['mail.mail'].sudo().create(create_values)
        mail.send()
        vals = {
            'email_from':email,
            'error':error,
        }   

        return request.render('aa_pendaftaran_online.akhir_html',vals)

    @http.route('/pendaftaran/form', type='http', auth="public", website=True)
    def chair_info(self, **post):
        jenjangs = [
            ('KB', 'KB'), 
            ('TKA', 'TK A'), 
            ('TKB', 'TK B'), 
            ('SD1', 'SD - Kelas 1'), 
            ('SD2', 'SD - Kelas 2'), 
            ('SD3', 'SD - Kelas 3'), 
            # ('SD4', 'SD - Kelas 4'), 
            # ('SD5', 'SD - Kelas 5'), 
            # ('SD6', 'SD - Kelas 6'), 
            ('SMP7', 'SMP - Kelas 7'), 
            # ('SMP8', 'SMP - Kelas 8'), 
            # ('SMP9', 'SMP - Kelas 9'), 
            # ('SMA10', 'SMA - Kelas 10'), 
            # ('SMA11', 'SMA - Kelas 11'), 
            # ('SMA12', 'SMA - Kelas 12'),
        ]
        return request.render('aa_pendaftaran_online.pendaftaran_html_form', {'jenjangs': jenjangs})


    def check_email(self, email):   
        if request.env['res.users'].search([('login','=',email)]):
            return True
        return False

    def validation_error(self, value):
        if value:
            raise ValidationError("Email sudah terdaftar")