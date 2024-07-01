# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountFiscalyearClose(models.TransientModel):
    _name = 'account.fiscalyear.close'
    _description = "Fiscalyear Close"

    fy_id = fields.Many2one('account.fiscalyear', 'Fiscal Year to close', required=True, help="Select a Fiscal year to close")
    fy2_id = fields.Many2one('account.fiscalyear', 'New Fiscal Year', required=True)
    journal_id = fields.Many2one('account.journal', 'Opening Entries Journal', required=True, domain="[('type','=','situation')]")
    period_id = fields.Many2one('account.period', 'Opening Entries Period', required=True)
    report_name = fields.Char('Name of new entries', required=True, help="Give name of the new entries", default="End of Fiscal Year Entry")

    @api.multi
    def data_save(self):

        obj_acc_move = self.env['account.move']
        obj_acc_move_line = self.env['account.move.line']
        obj_acc_account = self.env['account.account']
        obj_acc_journal_period = self.env['account.journal.period']
        for data in self:
            fy_id = data.fy_id
            fy2_id = data.fy2_id
            self._cr.execute("SELECT id FROM account_period WHERE date_stop < (SELECT date_start FROM account_fiscalyear WHERE id = %s)", (str(fy2_id.id),))
            fy_period_set = ','.join(map(lambda id: str(id[0]), self._cr.fetchall()))
            self._cr.execute("SELECT id FROM account_period WHERE date_start > (SELECT date_stop FROM account_fiscalyear WHERE id = %s)", (str(fy_id.id),))
            fy2_period_set = ','.join(map(lambda id: str(id[0]), self._cr.fetchall()))

            if not fy_period_set or not fy2_period_set:
                raise UserError(_('The periods to generate opening entries cannot be found.'))

            period = data.period_id
            new_fyear = fy2_id
            old_fyear = fy_id

            new_journal = data.journal_id
            company_id = new_journal.company_id.id

            if not new_journal.default_credit_account_id or not new_journal.default_debit_account_id:
                raise UserError(_('The journal must have default credit and debit account.'))
            if (not new_journal.centralisation) or new_journal.entry_posted:
                raise UserError(_('The journal must have centralized counterpart without the Skipping draft state option checked.'))

            #delete existing move and move lines if any
            move_ids = obj_acc_move.search([
                ('journal_id', '=', new_journal.id), ('period_id', '=', period.id)])
            if move_ids:
                move_line_ids = obj_acc_move_line.search([('move_id', 'in', move_ids.ids)])
                move_line_ids.remove_move_reconcile()
                move_line_ids.unlink()
                move_ids.unlink()
    
            self._cr.execute("SELECT id FROM account_fiscalyear WHERE date_stop < %s", (str(new_fyear.date_start),))
            result = self._cr.dictfetchall()
            fy_ids = [x['id'] for x in result]
            fiscalyear_ids = self.env['account.fiscalyear'].browse(fy_ids)
            query_get_clause = obj_acc_move_line.with_context({'fiscalyear': fiscalyear_ids})._query_get()
            query_get_clause_val = query_get_clause[2]
            query_line = "account_move_line.state = '%s'" % (query_get_clause_val[1])
            query_line += ' AND account_move_line.period_id in (SELECT id FROM account_period WHERE fiscalyear_id IN (%s))' % (query_get_clause_val[0])
            #create the opening move
            vals = {
                'name': '/',
                'ref': '',
                'period_id': period.id,
                'date': period.date_start,
                'journal_id': new_journal.id,
            }
            move_id = obj_acc_move.create(vals)

            #1. report of the accounts with defferal method == 'unreconciled'
            self._cr.execute('''
                SELECT a.id
                FROM account_account a
                LEFT JOIN account_account_type t ON (a.user_type_id = t.id)
                WHERE t.type not in ('view', 'consolidation')
                  AND a.company_id = %s
                  AND t.close_method = %s ORDER BY id asc''', (company_id, 'unreconciled', ))
            result = self._cr.dictfetchall()
            account_ids = [x['id'] for x in result]
            if account_ids:
                self._cr.execute('''
                    INSERT INTO account_move_line (
                         name, create_uid, create_date, write_uid, write_date,
                         statement_id, journal_id, currency_id, date_maturity,
                         partner_id, blocked, credit, state, debit,
                         ref, account_id, period_id, date, move_id, amount_currency,
                         quantity, product_id, company_id, fiscalyear_id)
                      (SELECT name, create_uid, create_date, write_uid, write_date,
                         statement_id, %s, currency_id, date_maturity, partner_id,
                         blocked, credit, 'draft', debit, ref, account_id,
                         %s, (%s) AS date, %s, amount_currency, quantity, product_id, company_id, %s
                       FROM account_move_line
                       WHERE account_id IN %s
                         AND ''' + query_line + '''
                         AND reconciled IS NULL)''', (new_journal.id, period.id, period.date_start, move_id.id, new_fyear.id, tuple(account_ids),))
    
                #We have also to consider all move_lines that were reconciled
                #on another fiscal year, and report them too
                self._cr.execute('''
                    INSERT INTO account_move_line (
                         name, create_uid, create_date, write_uid, write_date,
                         statement_id, journal_id, currency_id, date_maturity,
                         partner_id, blocked, credit, state, debit,
                         ref, account_id, period_id, date, move_id, amount_currency,
                         quantity, product_id, company_id, fiscalyear_id)
                      (SELECT
                         b.name, b.create_uid, b.create_date, b.write_uid, b.write_date,
                         b.statement_id, %s, b.currency_id, b.date_maturity,
                         b.partner_id, b.blocked, b.credit, 'draft', b.debit,
                         b.ref, b.account_id, %s, (%s) AS date, %s, b.amount_currency,
                         b.quantity, b.product_id, b.company_id, %s
                         FROM account_move_line b
                         WHERE b.account_id IN %s
                           AND b.reconciled IS NOT NULL
                           AND b.period_id IN ('''+fy_period_set+'''))''', (new_journal.id, period.id, period.date_start, move_id.id, new_fyear.id, tuple(account_ids),))
                self.invalidate_cache()

            #2. report of the accounts with defferal method == 'detail'
            self._cr.execute('''
                SELECT a.id
                FROM account_account a
                LEFT JOIN account_account_type t ON (a.user_type_id = t.id)
                WHERE t.type not in ('view', 'consolidation')
                  AND a.company_id = %s
                  AND t.close_method = %s ORDER BY id asc''', (company_id, 'detail', ))
            result = self._cr.dictfetchall()
            account_ids = [x['id'] for x in result]
            if account_ids:
                self._cr.execute('''
                    INSERT INTO account_move_line (
                         name, create_uid, create_date, write_uid, write_date,
                         statement_id, journal_id, currency_id, date_maturity,
                         partner_id, blocked, credit, state, debit,
                         ref, account_id, period_id, date, move_id, amount_currency,
                         quantity, product_id, company_id, fiscalyear_id)
                      (SELECT name, create_uid, create_date, write_uid, write_date,
                         statement_id, %s, currency_id, date_maturity, partner_id,
                         blocked, credit, 'draft', debit, ref, account_id,
                         %s, (%s) AS date, %s, amount_currency, quantity, product_id, company_id, %s
                       FROM account_move_line
                       WHERE account_id IN %s
                         AND ''' + query_line + ''')
                         ''', (new_journal.id, period.id, period.date_start, move_id.id, new_fyear.id, tuple(account_ids),))
                self.invalidate_cache()

            #3. report of the accounts with defferal method == 'balance'
            self._cr.execute('''
                SELECT a.id
                FROM account_account a
                LEFT JOIN account_account_type t ON (a.user_type_id = t.id)
                WHERE t.type not in ('view', 'consolidation')
                  AND a.company_id = %s
                  AND t.close_method = %s ORDER BY id asc''', (company_id, 'balance', ))
            result = self._cr.dictfetchall()
            account_ids = [x['id'] for x in result]
            query_1st_part = """
                    INSERT INTO account_move_line (
                         debit, credit, name, date, date_maturity, move_id, journal_id, period_id, fiscalyear_id, 
                         account_id, currency_id, amount_currency, company_id, state) VALUES
            """
            query_2nd_part = ""
            query_2nd_part_args = []
            for account in obj_acc_account.with_context({'fiscalyear': old_fyear}).browse(account_ids):
                company_currency_id = self.env.user.company_id.currency_id
                account_debit_line_ids = self.env['account.move.line'].search([('account_id','=', account.id),('debit','!=', 0.0)])
                account_debit = sum([line.debit for line in account_debit_line_ids])
                account_credit_line_ids = self.env['account.move.line'].search([('account_id','=', account.id),('credit','!=', 0.0)])
                account_credit = sum([line.credit for line in account_credit_line_ids])
                amount_balance = account_debit - account_credit
                if not company_currency_id.is_zero(abs(amount_balance)):
                    if query_2nd_part:
                        query_2nd_part += ','
                    query_2nd_part += "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    query_2nd_part_args += (amount_balance > 0 and amount_balance or 0.0,
                           amount_balance < 0 and -amount_balance or 0.0,
                           data.report_name,
                           period.date_start,
                           period.date_stop,
                           move_id.id,
                           new_journal.id,
                           period.id,
                           new_fyear.id,
                           account.id,
                           account.currency_id and account.currency_id.id or None,
                           account.foreign_balance if account.currency_id else 0.0,
                           account.company_id.id,
                           'draft')
            if query_2nd_part:
                self._cr.execute(query_1st_part + query_2nd_part, tuple(query_2nd_part_args))
                self.invalidate_cache()
            #validate and centralize the opening move
            move_id.validate()

            #create the journal.period object and link it to the old fiscalyear
            acc_journal_period_id = obj_acc_journal_period.search([('journal_id', '=', new_journal.id), ('period_id', '=', period.id)])
            if not acc_journal_period_id:
                acc_journal_period_id = obj_acc_journal_period.create({
                       'name': (new_journal.name or '') + ':' + (period.code or ''),
                       'journal_id': new_journal.id,
                       'period_id': period.id
                   })
            self._cr.execute('UPDATE account_fiscalyear ' \
                    'SET end_journal_period_id = %s ' \
                    'WHERE id = %s', (acc_journal_period_id.id, old_fyear.id))
            self.invalidate_cache()
            return {'type': 'ir.actions.act_window_close'}

