from odoo import api, fields, models
import os
from string import ascii_lowercase


class PrintRaportSekolah(models.AbstractModel):
    _name = "report.aa_kurikulum.template_raport_sekolah"

    @api.model
    def _get_report_values(self, docids, data=None):
        name = 'aa_kurikulum.template_raport_sekolah'
        report = self.env['ir.actions.report']._get_report_from_name(name)
        docs = self.env[report.model].browse(docids)
        lines = self.get_data()
        jumlah = self.jumlah(lines)
        rata = self.rata_rata(lines)
        list_alfabet = [x for x in ascii_lowercase]
        rowspan_keterampilan = self.rowspan_keterampilan(lines)
        return {
                'doc_ids': docids,
                'doc_model': report.model,
                'docs': self.env[report.model].browse(docids),
                'report_type': data.get('report_type') if data else '',
                'data': lines,
                'jumlah':jumlah,
                'rata':rata,
                'alfabet':list_alfabet,
                'rowspan1':rowspan_keterampilan,
        }

    def rowspan_keterampilan(self,lines):
        lines = [x for x in lines if x['tipe'] == 'pilihan']
        return len(lines)

    def jumlah(self,lines):
        hasil = sum([x['nilai'] for x in lines])
        return hasil

    def rata_rata(self,lines):
        hasil = sum([x['nilai'] for x in lines])/len(lines)
        return hasil

    def get_data(self):
        lines = [{'no': 1, 'tipe': 'wajib', 'mapel': 'pendidikan agama', 'kkm': 75, 'nilai': 85, 'terbilang': 'Delapan Puluh Lima'}, {'no': 2, 'tipe': 'wajib', 'mapel': 'pendidikan kewarganegaraan', 'kkm': 75, 'nilai': 85, 'terbilang': 'Delapan Puluh Lima'}, {'no': 3, 'tipe': 'wajib', 'mapel': 'bahasa dan sastra indonesia', 'kkm': 75, 'nilai': 81, 'terbilang': 'Delapan Puluh Satu'}, {'no': 4, 'tipe': 'wajib', 'mapel': 'bahasa inggris', 'kkm': 75, 'nilai': 83, 'terbilang': 'Delapan Puluh Tiga'}, {'no': 5, 'tipe': 'wajib', 'mapel': 'matematika', 'kkm': 75, 'nilai': 89, 'terbilang': 'Delapan Puluh Sembilan'}, {'no': 6, 'tipe': 'wajib', 'mapel': 'ilmu pengetahuan alam', 'kkm': 75, 'nilai': 85, 'terbilang': 'Delapan Puluh Lima'}, {'no': 7, 'tipe': 'wajib', 'mapel': 'ilmu pengetahuan sosial', 'kkm': 75, 'nilai': 85, 'terbilang': 'Delapan Puluh Lima'}, {'no': 8, 'tipe': 'wajib', 'mapel': 'seni dan budaya', 'kkm': 75, 'nilai': 91, 'terbilang': 'Sembilan Puluh Satu'}, {'no': 9, 'tipe': 'wajib', 'mapel': 'pendidikan jasmani', 'kkm': 75, 'nilai': 84, 'terbilang': 'Delapan Puluh Empat'}, {'no': 10, 'tipe': 'pilihan', 'mapel': 'keterampilan', 'kkm': 75, 'nilai': 85, 'terbilang': 'Delapan Puluh Lima'}, {'no': 11, 'tipe': 'pilihan', 'mapel': 'teknologi informasi', 'kkm': 75, 'nilai': 92, 'terbilang': 'Sembilan Puluh Dua'}, {'no': 12, 'tipe': 'mulok', 'mapel': 'rmr', 'kkm': 75, 'nilai': 90, 'terbilang': 'Sembilan Puluh'}]
        return lines

    def terbilang_(self, n):
        n = abs(int(n))

        satuan = [
            "",
            "Satu",
            "Dua",
            "Tiga",
            "Empat",
            "Lima",
            "Enam",
            "Tujuh",
            "Delapan",
            "Sembilan",
            "Sepuluh",
            "Sebelas",
        ]

        if n >= 0 and n <= 11:
            hasil = [satuan[n]]
        elif n >= 12 and n <= 19:
            hasil = self.terbilang_(n % 10) + ["Belas"]
        elif n >= 20 and n <= 99:
            hasil = (
                self.terbilang_(n / 10) + ["Puluh"] + self.terbilang_(n % 10)
            )
        elif n >= 100 and n <= 199:
            hasil = ["Seratus"] + self.terbilang_(n - 100)
        elif n >= 200 and n <= 999:
            hasil = (
                self.terbilang_(n / 100) + ["Ratus"] + self.terbilang_(n % 100)
            )
        elif n >= 1000 and n <= 1999:
            hasil = ["Seribu"] + self.terbilang_(n - 1000)
        elif n >= 2000 and n <= 999999:
            hasil = (
                self.terbilang_(n / 1000)
                + ["Ribu"]
                + self.terbilang_(n % 1000)
            )
        elif n >= 1000000 and n <= 999999999:
            hasil = (
                self.terbilang_(n / 1000000)
                + ["Juta"]
                + self.terbilang_(n % 1000000)
            )
        else:
            hasil = (
                self.terbilang_(n / 1000000000)
                + ["Milyar"]
                + self.terbilang_(n % 100000000)
            )
        return hasil

    def terbilang(self, n):
        if n == 0:
            return "Nol"
        t = self.terbilang_(n)
        while "" in t:
            t.remove("")
        return " ".join(t)
