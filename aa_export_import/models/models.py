from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import csv
import codecs
import base64
from io import StringIO, BytesIO
from odoo.tools import float_is_zero, pycompat



class EksportImport(models.TransientModel):
    _name = "eksport.import"

    type = fields.Selection((('eks','Export'), ('imp','Import')), 'Type', default='eks', required=True)
    tabel = fields.Many2one('ir.model', 'Tabel Name', required=True)
    name = fields.Char('File Name')
    data_file = fields.Binary('File')

    def eksport_excel(self):
        set_ids = self.env[self.tabel.model].search([])
        if not set_ids :
            raise UserError(('Data tidak ditemukan !'))

        data = set_ids.read()
        value = [d.values() for d in data]

        fecfile = BytesIO()
        writer = pycompat.csv_writer(fecfile, delimiter=';', lineterminator='\n')

        writer.writerow([k.upper() for k in data[0].keys()])

        for row in value:
            baris = list(row)
            for e in baris:
                if isinstance(e, bytes):
                    baris[baris.index(e)] = 'image'
                elif isinstance(e, tuple):
                    baris[baris.index(e)] = e[1]
                elif isinstance(e, datetime):
                    baris[baris.index(e)] = datetime.strftime(e, "%d %B %Y")
            writer.writerow(baris)

        fecvalue = fecfile.getvalue()
        fecfile.close()

        self.write({'data_file': base64.encodestring(fecvalue), 'name': '%s.csv' % self.tabel.name})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'eksport.import',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    def import_excel(self):
        if not self.data_file:
            raise UserError(('Silahkan memilih file yang akan diimport !'))

        csv_data = base64.b64decode(self.data_file)
        data_file = StringIO(csv_data.decode("utf-8"))
        data_file.seek(0)
        csv_reader = list(csv.reader(data_file, delimiter=';'))

        col = csv_reader.pop(0) #[0].split('\t')

        res = {}
        for row in csv_reader:
            for x in range(0, len(col)):
                r = row[x]
                if r.upper() == 'FALSE':
                    r = False
                elif r.upper() == 'TRUE':
                    r = True
                res[col[x]] = r

            # print (self.tabel.model, '############################', res)

            self.env[self.tabel.model].create(res)

        return {'type': 'ir.actions.act_window_close'}
    
