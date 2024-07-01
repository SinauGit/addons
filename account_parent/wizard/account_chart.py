# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 Steigend IT Solutions
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################

from odoo import models, fields, api,_
from odoo.tools import safe_eval
import time


class OpenAccountChart(models.TransientModel):
    """
    For Chart of Accounts
    """
    _name = "account.open.chart"
    _description = "Account Open chart"
    
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries'),
                                    ], string='Target Moves', required=True, default='posted')
    parent_needed = fields.Boolean('Parent Grouping Needed')
    
    def _build_contexts(self):
        self.ensure_one()
        result = {}
        result['state'] = self.target_move or ''
        result['date_from'] = self.date_from or False
        result['date_to'] = self.date_to or False
        result['strict_range'] = True if result['date_from'] else False
        result['show_parent_account'] = True
        result['company_id'] = self.company_id.id
        result['active_id'] = self.id
        return result
    
    @api.model
    def build_domain(self, wiz_id=None, account_id=None):
        result = []
        context = dict(self.env.context)
        if wiz_id:
            context.update(self.browse(wiz_id)._build_contexts())
        result = self.env['account.account'].with_context(context)._move_domain_get()
        if account_id:
            result.append(('account_id','child_of',[account_id]))
        return result

    @api.multi
    def account_chart_open_window(self):
        """
        Opens chart of Accounts
        @return: dictionary of Open account chart window on given date(s) and all Entries or posted entries
        """
        self.ensure_one()
        used_context = {'show_parent_account': True,
                        'company_id': self.company_id.id,
                        'active_id': self.id
                        }
        self  = self.with_context(used_context)
        if self.env['account.account'].search([('parent_id','!=',False)],limit=1):
            result = self.env.ref('account_parent.open_view_account_tree').read([])[0]
        else:
            result = self.env.ref('account.action_account_form').read([])[0]
        result_context = safe_eval(result.get('context','{}')) or {}
        used_context.update(result_context)
        result['context'] = str(used_context)
        return result

    @api.model
    def get_all_lines(self, line_id=False, level=1):
        self.ensure_one()
        result = []
        for line in self.get_lines(self.id, line_id=line_id, level=level):
            result.append(line)
            result.extend(self.get_all_lines(line_id=line['model_id'], level=line['level']+1))
        return result

    @api.model
    def get_lines(self, wiz_id=None, line_id=None, **kw):
        context = dict(self.env.context)
        if wiz_id:
            context.update(self.browse(wiz_id)._build_contexts())
        model_id = False
        level = 1
        if kw:
            level = kw.get('level', 0)
            model_id = kw.get('model_id')
        res = []
        accounts = self.env['account.account'].with_context(context).search([('company_id','=',context.get('company_id',False)),
                                                                             ('parent_id','=',line_id)])
        res = self._lines(wiz_id, line_id,  model_id=model_id, level=level, obj_ids=accounts)
        reverse_sort = False
        final_vals = sorted(res, key=lambda v: v['code'], reverse=reverse_sort)
        lines = self.final_vals_to_lines(final_vals, level)
        return lines

    @api.model
    def get_links(self, move_line):
        res_model = ''
        ref = ''
        res_id = False
        if move_line.picking_id:
            res_model = 'stock.picking'
            res_id = move_line.picking_id.id
            ref = move_line.picking_id.name
        elif move_line.move_id.inventory_id:
            res_model = 'stock.inventory'
            res_id = move_line.move_id.inventory_id.id
            ref = 'Inv. Adj.: ' + move_line.move_id.inventory_id.name
        elif move_line.move_id.scrapped and move_line.move_id.scrap_ids:
            res_model = 'stock.scrap'
            res_id = move_line.move_id.scrap_ids[0].id
            ref = move_line.move_id.scrap_ids[0].name
        return res_model, res_id, ref

    @api.model
    def _amount_to_str(self, value, currency):
        """ workaround to apply the float rounding logic of t-esc on data prepared server side """
        return self.env['ir.qweb.field.monetary'].value_to_html(value, {'display_currency': currency})

    @api.model
    def _m2o_to_str(self, value):
        return self.env['ir.qweb.field.many2one'].value_to_html(value,{}) or ''

    
    
    def make_dict_head(self, level, parent_id,wiz_id=False, account=False):
        data = []
        data = [{
            'id': account.id,
            'wiz_id': wiz_id,
            'level': level,
            'unfoldable': account.user_type_id.type == 'view' and True or False,
            'model_id': account.id,
            'parent_id': parent_id,
            'code': account.code,
            'name': account.name,
            'type': self._m2o_to_str(account.user_type_id),
            'ttype': account.user_type_id.type,
            'currency': self._m2o_to_str(account.currency_id),
            'company': self._m2o_to_str(account.company_id),
            'debit': self._amount_to_str(account.debit, account.company_id.currency_id),
            'credit': self._amount_to_str(account.credit, account.company_id.currency_id),
            'balance': self._amount_to_str(account.balance, account.company_id.currency_id),
            }]
        return data
    
    def make_xls_dict_head(self, level, parent_id,wiz_id=False, account=False):
        data = []
        data = [{
            'id': account.id,
            'wiz_id': wiz_id,
            'level': level,
            'unfoldable': account.user_type_id.type == 'view' and True or False,
            'model_id': account.id,
            'parent_id': parent_id,
            'code': account.code,
            'name': account.name,
            'type': self._m2o_to_str(account.user_type_id),
            'ttype': account.user_type_id.type,
            'currency': self._m2o_to_str(account.currency_id),
            'company': self._m2o_to_str(account.company_id),
            'debit': account.debit,
            'credit': account.credit,
            'balance': account.balance,
            }]
        return data

    @api.model
    def final_vals_to_lines(self, final_vals, level):
        lines = []
        for data in final_vals:
            lines.append({
                'id': data['id'],
                'wiz_id': data['wiz_id'],
                'model_id': data['model_id'],
                'parent_id': data['parent_id'],
                'type': data.get('ttype'),
                'name': _(data.get('name')),
                'columns': [data.get('code'),
                            data.get('name'),
                            data.get('type'),
                            data.get('currency',''),
#                             data.get('company', ''),
                            data.get('debit'),
                            data.get('credit'),
                            data.get('balance')],
                'level': level,
                'unfoldable': data['unfoldable'],
            })
        return lines
    
    @api.model
    def _lines(self, wiz_id=None, line_id=None, model_id=False, level=0, obj_ids=[], **kw):
        context = self._context
        final_vals = []
        if 'output_format' in context.keys() and context.get('output_format') == 'xls':
            for account in obj_ids:
                final_vals += self.make_xls_dict_head(level,wiz_id=wiz_id,  parent_id=line_id, account=account)
        else:
            for account in obj_ids:
                final_vals += self.make_dict_head(level,wiz_id=wiz_id,  parent_id=line_id, account=account)
        return final_vals

    @api.model
    def get_pdf_lines(self, wiz_id):
        lines = self.browse(wiz_id).get_all_lines()
        return lines

    def get_pdf(self, wiz_id):
        lines = self.with_context(print_mode=True).get_pdf_lines(wiz_id)
        user_context = self.browse(wiz_id)._build_contexts()
        heading = self.env['res.company'].browse(user_context.get('company_id')).display_name
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        rcontext = {
            'mode': 'print',
            'base_url': base_url,
        }
        user_context.update(rcontext)
        self = self.with_context(user_context)
        body = self.env['ir.ui.view'].render_template(
            "account_parent.report_coa_heirarchy_print",
            values=dict(rcontext, 
                        lines=lines,
                        heading=heading,
                        user_data=user_context, 
                        time=time,
                        context_timestamp=lambda t: fields.Datetime.context_timestamp(self.with_context(tz=self.env.user.tz), t),
                        report=self, 
                        context=self),
        )

        header = self.env['ir.actions.report'].render_template("web.internal_layout", values=rcontext)
        header = self.env['ir.actions.report'].render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=header))

        return self.env['ir.actions.report']._run_wkhtmltopdf(
            [body],
            header=header,
            landscape=True,
            specific_paperformat_args={'data-report-margin-top': 10, 'data-report-header-spacing': 10}
        )
#         docargs = {
#             'doc_ids': self.browse(wiz_id).ids,
#             'doc_model': self.model,
#             'data': user_context,
#             'docs': self.browse(wiz_id),
#             'time': time,
#             'lines': lines,
#             'heading': heading,
#         }
#         return self.env['report'].render('account.report_generalledger', docargs)

    def _get_html(self):
        result = {}
        rcontext = {}
        context = self.env.context
        if context.get('active_id') and context.get('active_model') == 'account.open.chart':
            user_context = self.browse(context.get('active_id'))._build_contexts()
            rcontext['lines'] = self.with_context(context).get_lines(wiz_id=context.get('active_id'))
            rcontext['heading'] = self.env['res.company'].browse(user_context.get('company_id')).display_name
        result['html'] = self.env.ref('account_parent.report_coa_heirarchy').render(rcontext)
        return result

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(given_context)._get_html()


# class WizardMultiChartsAccounts(models.TransientModel):
#     _inherit = 'wizard.multi.charts.accounts'
# 
#     @api.multi
#     def execute(self):
#         res = super(WizardMultiChartsAccounts, self).execute()
#         self.chart_template_id.update_generated_account({},self.code_digits,self.company_id)
#         return res
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
