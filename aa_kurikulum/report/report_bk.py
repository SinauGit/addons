from odoo import api, fields, models
 
class CourseXlsx(models.AbstractModel):
    _name = 'report.aa_kurikulum.report_pelanggaran'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, obj):
        sheet = workbook.add_worksheet('Travel %s' % obj.nama)
        text_top_style = workbook.add_format({'font_size': 12, 'bold': True ,'font_color' : 'white', 'bg_color': '#f00a0d', 'valign': 'vcenter', 'text_wrap': True})
        text_header_style = workbook.add_format({'font_size': 12, 'bold': True ,'font_color' : 'white', 'bg_color': '#f00a0d', 'valign': 'vcenter', 'text_wrap': True, 'align': 'center'})
        text_style = workbook.add_format({'font_size': 12, 'valign': 'vcenter', 'text_wrap': True, 'align': 'center'})
        number_style = workbook.add_format({'num_format': '#,##0', 'font_size': 12, 'align': 'right', 'valign': 'vcenter', 'text_wrap': True})
        
        
        text_style.set_border(3)
        number_style.set_border(3)
        # sheet.write(1, 2, "MANIFEST", text_top_style)
        # sheet.write(1, 4, obj.nama)
        
        
        row = 3
        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 17, 20)
        header = ['NO', 'Nama Santri', 'Pelanggaran', 'Waktu Pelanggaran', 'Point/Sanksi','Keterangan']
        sheet.write_row(row, 0, header, text_header_style)
        
        
        no_list = []
        nama = []
        pelanggaran = []
        waktu_pelanggaran = []
        point = []
        keterangan = []
        # no_passpor = []
        # tanggal_berlaku = []
        # tanggal_expired = []
        # imigrasi = []
        # umur = []
        # noktp = []
        # order = []
        # tipe_kamar = []
        # room_leader = []
        # no_room = []
        # alamat = []
        
        
        no = 1
        for x in obj:
            # no_list.append(no)
            # nama.append(x.siswa_id)
            # pelanggaran.append(x.info)
            # waktu_pelanggaran.append(x.waktu_pelanggaran)
            # point.append(x.point) 
            # keterangan.append(x.keterangan) 
            # no_passpor.append(x.no_passpor)
            # tanggal_berlaku.append(x.tanggal_berlaku.strftime('%d %B %Y'))
            # tanggal_expired.append(x.tanggal_expired.strftime('%d %B %Y'))
            # imigrasi.append(x.imigrasi)
            # umur.append(x.umur) 
            # noktp.append(x.noktp)
            # order.append(x.sale_id.name)
            # tipe_kamar.append(x.tipe_kamar)
            # room_leader.append('-')
            # no_room.append('-')
            # alamat.append(x.city)
            no+=1
            
        row += 1
        sheet.write_column(row, 0, no_list, text_style)
        sheet.write_column(row, 1, nama, text_style)
        sheet.write_column(row, 2, pelanggaran, text_style)
        sheet.write_column(row, 3, waktu_pelanggaran, text_style)
        sheet.write_column(row, 4, point, text_style)
        sheet.write_column(row, 5, keterangan, text_style)
        # sheet.write_column(row, 6, no_passpor, text_style)
        # sheet.write_column(row, 7, tanggal_berlaku, text_style)
        # sheet.write_column(row, 8, tanggal_expired, text_style)
        # sheet.write_column(row, 9, imigrasi, text_style)
        # sheet.write_column(row, 10, umur, text_style)
        # sheet.write_column(row, 11, noktp, text_style)
        # sheet.write_column(row, 12, order, text_style)
        # sheet.write_column(row, 13, tipe_kamar, text_style)
        # sheet.write_column(row, 14, room_leader, text_style)
        # sheet.write_column(row, 15, no_room, text_style)
        # sheet.write_column(row, 16, alamat, text_style)
        
        
        # b = no
        # row = 8 + b
        # header = ['NO','AIRLINE','DEPARTURE DATE','DEPARTURE CITY', 'ARIVAL CITY']
        # sheet.write_row(row, 2, header, text_header_style)
        
        # nomor = []
        # airline = []
        # departure_date = []
        # departure_city = []
        # arrival_city = []
        
        # no = 1
        # for x in obj.airline_line: 
        #     nomor.append(no)
        #     airline.append(x.partner_id.name)
        #     departure_date.append(x.berangkat_date.strftime('%d %B %Y'))
        #     departure_city.append(x.kota_asal)
        #     arrival_city.append(x.kota_tujuan)
        #     no +=1
        
        # row+=1
        # sheet.write_column(row, 2, nomor, text_style)
        # sheet.write_column(row, 3, airline, text_style)
        # sheet.write_column(row, 4, departure_date, text_style)
        # sheet.write_column(row, 5, departure_city, text_style)
        # sheet.write_column(row, 6, arrival_city, text_style)
        
        
        
        
        
        
        
        
        