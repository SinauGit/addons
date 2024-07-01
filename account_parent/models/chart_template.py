# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 Steigend IT Solutions
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################

from odoo import api, fields, models, _

class AccountAccountTemplate(models.Model):
    _inherit = "account.account.template"
    
    parent_id = fields.Many2one('account.account.template','Parent Account',ondelete="set null")
        
class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"
    
    @api.multi
    def generate_account(self, tax_template_ref, acc_template_ref, code_digits, company):
        account_tmpl_pool = self.env['account.account.template']
        account_pool = self.env['account.account']
        account_template_account_dict = super(AccountChartTemplate, self).generate_account(tax_template_ref, acc_template_ref, code_digits, company)
        account_template_objs = account_tmpl_pool.browse(account_template_account_dict.keys())
        for account_template_id, account_id in account_template_account_dict.items():
            account_template_obj = account_tmpl_pool.browse(account_template_id)
#             account_template_obj.update_account_with_parent(account_template_account_dict[account_template_obj.id],company)
            if not account_template_obj.parent_id:
                continue
            account_parent_id = account_template_account_dict.get(account_template_obj.parent_id.id,False)
            account_pool.browse(account_id).write({'parent_id': account_parent_id})
        return account_template_account_dict
    
    @api.multi
    def update_generated_account(self, tax_template_ref=[], code_digits=1, company=False,importing_parent=False):
        """ This method for generating parent accounts from templates.

            :param tax_template_ref: Taxes templates reference for write taxes_id in account_account.
            :param code_digits: number of digits the accounts code should have in the COA
            :param company: company the wizard is running for
            :returns: return acc_template_ref for reference purpose.
            :rtype: dict
        """
        
        account_tmpl_obj = self.env['account.account.template']
        account_obj = self.env['account.account']
        view_liquidity_type = self.env.ref('account_parent.data_account_type_view')
        if not importing_parent:
#             parent_account_id = account_obj.with_context({'show_parent_account':True}).search([('parent_id','=',False),
#                                                              ('user_type_id','=',view_liquidity_type.id),('company_id','=',company.id)], limit=1)
#             account = account_obj.search([('code','=',"999999"),('company_id','=',company.id)])
#             account and account.with_context({'company_id':company.id}).write({'parent_id':parent_account_id.id})
            return True
        self.ensure_one()
        if not company:
            company = self.env.user.company_id
        account_tmpl_obj = self.env['account.account.template']
        account_obj = self.env['account.account']
        acc_templates = account_tmpl_obj.search([('nocreate', '!=', True), ('chart_template_id', '=', self.id),
                                                ], order='id')
        code_account_dict = {}
        
        for account_template in acc_templates:
            tax_ids = []
            for tax in account_template.tax_ids:
                tax_ids.append(tax_template_ref[tax.id])

            code_main = account_template.code and len(account_template.code) or 0
            code_acc = account_template.code or ''
            if code_main > 0 and code_main <= code_digits:
                code_acc =  str(code_acc) + (str('0'*(code_digits-code_main)))
            if account_template.user_type_id.id == view_liquidity_type.id:
                new_code = account_template.code
            else:
                new_code = code_acc
            new_account = self.env['account.account'].with_context({'show_parent_account':True}).search([('code','=',new_code),('company_id','=',company.id)], limit=1)
            if not new_account:
                vals = {
                    'name': account_template.name,
                    'currency_id': account_template.currency_id and account_template.currency_id.id or False,
                    'code':new_code ,
                    'user_type_id': account_template.user_type_id and account_template.user_type_id.id or False,
                    'reconcile': account_template.reconcile,
                    'note': account_template.note,
                    'tax_ids': [(6, 0, tax_ids)],
                    'company_id': company.id,
                    'tag_ids': [(6, 0, [t.id for t in account_template.tag_ids])],
                    'group_id': account_template.group_id.id or False,
                }
                new_account_id = self.create_record_with_xmlid(company, account_template, 'account.account', vals)
                new_account = self.env['account.account'].with_context({'show_parent_account':True}).browse(new_account_id)
#                 new_account = self.env['account.account'].create(vals)
#             account_template.update_account_with_parent(new_account.id,company)
            if new_code not in code_account_dict:
                code_account_dict[new_code] = new_account
        if company.bank_account_code_prefix:
            if code_account_dict.get(company.bank_account_code_prefix,False):
                parent_account_id = code_account_dict.get(company.bank_account_code_prefix,False)
            else:
                parent_account_id = account_obj.with_context({'show_parent_account':True}).search([
                    ('code','=',company.bank_account_code_prefix),
                    ('user_type_id.type', '=', 'view'),
                    ('company_id','=',company.id)], limit=1)
            account = account_obj.search([('code','like',"%s%%"%company.bank_account_code_prefix),
                                                              ('id','!=',parent_account_id.id),('company_id','=',company.id)])
            account and account.write({'parent_id':parent_account_id.id})
        if company.cash_account_code_prefix:
            if code_account_dict.get(company.cash_account_code_prefix,False):
                parent_account_id = code_account_dict.get(company.cash_account_code_prefix,False)
            else:
                parent_account_id = account_obj.with_context({'show_parent_account':True}).search([
                    ('code','=',company.cash_account_code_prefix),
                    ('user_type_id.type', '=', 'view'),
                    ('company_id','=',company.id)], limit=1)
            
            account = account_obj.search([('code','like',"%s%%"%company.cash_account_code_prefix),
                                                              ('id','!=',parent_account_id.id),('company_id','=',company.id)])
            account and account.write({'parent_id':parent_account_id.id})
        if company.transfer_account_code_prefix:
            if code_account_dict.get(company.transfer_account_code_prefix,False):
                parent_account_id = code_account_dict.get(company.transfer_account_code_prefix,False)
            else:
                parent_account_id = account_obj.with_context({'show_parent_account':True}).search([
                    ('code','=',company.transfer_account_code_prefix),
                    ('user_type_id.type', '=', 'view'),
                    ('company_id','=',company.id)], limit=1)
            
            account = account_obj.search([('code','like',"%s%%"%company.transfer_account_code_prefix),
                                                              ('id','!=',parent_account_id.id),('company_id','=',company.id)])
            account and account.write({'parent_id':parent_account_id.id})

#         parent_account_id = account_obj.with_context({'show_parent_account':True}).search([('parent_id','=',False),
#                                                              ('user_type_id','=',view_liquidity_type.id),('company_id','=',company.id)], limit=1)
#         account = account_obj.search([('code','=',"999999"),('company_id','=',company.id)])
#         account and account.with_context({'company_id':company.id}).write({'parent_id':parent_account_id.id})
        
#         all_acc_templates = acc_templates.with_context({'company_id':company.id})
        ir_model_data = self.env['ir.model.data']
        for account_template in acc_templates:
            if not account_template.parent_id:
                continue
            template_xml_obj = ir_model_data.search([('model', '=', account_template._name), ('res_id', '=', account_template.id)])
            account_xml_id = "%s.%s_%s" % (template_xml_obj.module, company.id, template_xml_obj.name)
            account = self.env.ref(account_xml_id, raise_if_not_found=False)
            parent_template_xml_obj = ir_model_data.search([('model', '=', account_template._name), ('res_id', '=', account_template.parent_id.id)])
            parent_account_xml_id = "%s.%s_%s" % (parent_template_xml_obj.module, company.id, parent_template_xml_obj.name)
            parent_account = self.env.ref(parent_account_xml_id, raise_if_not_found=False)
            account.write({'parent_id':parent_account.id})
        return True
    
    def load_for_current_company(self, sale_tax_rate, purchase_tax_rate):
        res = super(AccountChartTemplate, self).load_for_current_company(sale_tax_rate=sale_tax_rate, purchase_tax_rate=purchase_tax_rate)
        self.update_generated_account({},self.code_digits,self.env.user.company_id)
        return res
    