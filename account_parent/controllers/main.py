# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import html_escape,pycompat
from odoo.addons.web.controllers.main import ExcelExport

import json
import re
import io
import datetime
from lxml.etree import fromstring
try:
    import xlwt
except ImportError:
    xlwt = None

class CoAReportController(http.Controller):

    @http.route('/account_parent/<string:output_format>/<string:report_name>/<int:report_id>', type='http', auth='user')
    def report(self, output_format, report_name, token, report_id=False, **kw):
        coa = request.env['account.open.chart'].browse(report_id)
#         line_data = json.loads(kw['data'])
        try:
            if output_format == 'pdf':
                response = request.make_response(
                    coa.with_context(active_id=report_id).get_pdf(report_id),
                    headers=[
                        ('Content-Type', 'application/pdf'),
                        ('Content-Disposition', 'attachment; filename=coa_report.pdf;')
                    ]
                )
                response.set_cookie('fileToken', token)
                return response
        except Exception as e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))
        
class ExcelExportView(ExcelExport):
    
    def __getattribute__(self, name):
        if name == 'fmt':
            raise AttributeError()
        return super(ExcelExportView, self).__getattribute__(name)
    
    #Modified base form_data and add bold and font size based on our design
    def from_data(self, fields, rows):
        if len(rows) > 65535:
            raise UserError(_('There are too many rows (%s rows, limit: 65535) to export as Excel 97-2003 (.xls) format. Consider splitting the export.') % len(rows))

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        style = xlwt.easyxf('align: wrap yes')
        font = xlwt.Font()
        font.bold = True
        font.height = 300
        style.font = font

        for i, fieldname in enumerate(fields):
            worksheet.write(0, i, fieldname, style)
            worksheet.col(i).width = 8000 # around 220 pixels

        base_style = xlwt.easyxf('align: wrap yes')
        date_style = xlwt.easyxf('align: wrap yes', num_format_str='YYYY-MM-DD')
        datetime_style = xlwt.easyxf('align: wrap yes', num_format_str='YYYY-MM-DD HH:mm:SS')

        for row_index, row in enumerate(rows):
            for cell_index, cell_value in enumerate(row):
                cell_style = base_style

                if isinstance(cell_value, bytes) and not isinstance(cell_value, pycompat.string_types):
                    # because xls uses raw export, we can get a bytes object
                    # here. xlwt does not support bytes values in Python 3 ->
                    # assume this is base64 and decode to a string, if this
                    # fails note that you can't export
                    try:
                        cell_value = pycompat.to_text(cell_value)
                    except UnicodeDecodeError:
                        raise UserError(_("Binary fields can not be exported to Excel unless their content is base64-encoded. That does not seem to be the case for %s.") % fields[cell_index])
                if isinstance(cell_value, pycompat.string_types):
                    cell_value = re.sub("\r", " ", pycompat.to_text(cell_value))
                    # Excel supports a maximum of 32767 characters in each cell:
                    cell_value = cell_value[:32767]
                elif isinstance(cell_value, datetime.datetime):
                    cell_style = datetime_style
                elif isinstance(cell_value, datetime.date):
                    cell_style = date_style
                font = xlwt.Font()
                font.bold = False
                cell_style.font = font
                if row_index + 1 in  [2,5]:
                    font = xlwt.Font()
                    font.bold = True
                    cell_style.font = font
                worksheet.write(row_index + 1, cell_index, cell_value, cell_style)

        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return data
    
#     def remove_extra_data(self, raw_data, currency_symbol):
#         if currency_symbol in raw_data:
#             raw_data = raw_data.replace(currency_symbol,'')
#         if '$\xa0' in raw_data:
#             raw_data = raw_data.split('$\xa0')[1]
#         raw_data = raw_data.rstrip().strip()
#         value = fromstring(raw_data).text.replace(',','').replace('\ufeff','')
#         float_value = float(value)
#         return float_value
        
    @http.route('/account_parent_xls/<string:output_format>/<string:report_name>/<int:report_id>', type='http', auth='user')
    def export_xls_view_parent(self, output_format, data, token, report_id=False, **kw):
        data = json.loads(data)
#         wiz_id = data.get('wiz_id', [])
#         line_data = data.get('report_data', [])
        user_context = request.env['account.open.chart'].browse(report_id)._build_contexts()
        lines = request.env['account.open.chart'].with_context(print_mode=True, output_format=output_format).get_pdf_lines(report_id)
        company = request.env['res.company'].browse(user_context.get('company_id')).name
        currency_symbol = request.env['res.company'].browse(user_context.get('company_id')).currency_id.symbol
        date_from = user_context.get('date_from')
        date_to = user_context.get('date_to')
        if user_context.get('state') == "posted":
            move = "All Posted Entries"
        else:
            move="All Entries"
        row_data = [['','','','','','',], ['Company:','Target Moves:','Date from:','Date to:',], [company, move, date_from, date_to], ['','','','','','','',], ['Code', 'Name', 'Type', 'Currency', 'Debit', 'Credit', 'Balance']]
        for line in lines:
            data = line.get('columns')
            code = data[0]
            name = data[1]
            type = data[2]
            currency = data[3]
            debit = data[4]
            credit = data[5]
            balance = data[6]
            row_data.append([code, name, type, currency, debit, credit, balance])
        columns_headers = ['','','Chart Of Accounts','','']
        rows = row_data
        return request.make_response(
            self.from_data(columns_headers, rows),
            headers=[
                        ('Content-Type', self.content_type),
                        ('Content-Disposition', 'attachment; filename=coa_report.xls;')
            ],
            cookies={'fileToken': token}
        )
