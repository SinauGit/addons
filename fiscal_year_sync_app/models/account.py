# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from datetime import date

class AccountAccountType(models.Model):
    _inherit = "account.account.type"
    _description = "Account Type"

    close_method = fields.Selection([('none', 'None'),
                                     ('balance', 'Balance'),
                                     ('detail', 'Detail'),
                                     ('unreconciled', 'Unreconciled')], 
                                     'Deferral Method', default='none',
                                     help="""Set here the method that will be used to generate the end of year journal entries for all the accounts of this type.""")

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    @api.depends('date_invoice')
    def _compute_get_period(self):
        for record in self:
            if record.date_invoice:
                today = record.date_invoice
                period_ids = self.env['account.period'].search([('special','=',False), ('date_start','<=',today), ('date_stop','>=',today)], limit=1)
                record.period_id = period_ids

    period_id = fields.Many2one('account.period', string='Period', store=True, compute='_compute_get_period', readonly=True, states={'draft': [('readonly', False)]})
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Fiscal Year', related='period_id.fiscalyear_id', store=True)

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']

        for inv in self:
            if inv.period_id.state == 'done':
                raise UserError(_('You can not create account invoice in a closed period %s') % (inv.period_id.name))
            if inv.fiscalyear_id.state == 'done':
                raise UserError(_('%s is already closed') % (inv.fiscalyear_id.name))
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids.filtered(lambda line: line.account_id):
                raise UserError(_('Please add at least one invoice line.'))
            if inv.move_id:
                continue

            if not inv.date_invoice:
                inv.write({'date_invoice': fields.Date.context_today(self)})
            if not inv.date_due:
                inv.write({'date_due': inv.date_invoice})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.compute_invoice_totals(company_currency, iml)

            name = inv.name or ''
            if inv.payment_term_id:
                totlines = inv.payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
                res_amount_currency = total_currency
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency._convert(t[1], inv.currency_id, inv.company_id, inv._get_currency_rate_date() or fields.Date.today())
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            line = inv.finalize_invoice_move_lines(line)
            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': inv.journal_id.id,
                'date': date,
                'narration': inv.comment,
            }
            period = inv.period_id
            if not period:
                period = period.find(date)
            if period:
                move_vals['period_id'] = period.id
                for i in line:
                    i[2]['period_id'] = period.id
            move = account_move.create(move_vals)
            # Pass invoice in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post(invoice = inv)
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
                'period_id': period.id,
            }
            inv.write(vals)
        return True

class AccountJournal(models.Model):
    _inherit = "account.journal"
    _description = "Journal"

    type = fields.Selection([
            ('sale', 'Sale'),
            ('purchase', 'Purchase'),
            ('cash', 'Cash'),
            ('bank', 'Bank'),
            ('general', 'Miscellaneous'),
            ('situation', 'Opening/Closing Situation')
        ], required=True,
        help="Select 'Sale' for customer invoices journals.\n"\
        "Select 'Purchase' for vendor bills journals.\n"\
        "Select 'Cash' or 'Bank' for journals that are used in customer or vendor payments.\n"\
        "Select 'General' for miscellaneous operations journals.\n"\
        "Select 'Opening/Closing Situation' for entries generated for new fiscal years.")
    centralisation = fields.Boolean('Centralized Counterpart', help="Check this box to determine that each entry of this journal won't create a new counterpart but will share the same counterpart. This is used in fiscal year closing.")
    entry_posted = fields.Boolean('Autopost Created Moves', help='Check this box to automatically post entries of this journal. Note that legally, some entries may be automatically posted when the source document is validated (Invoices), whatever the status of this field.')

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    @api.depends('date')
    def _compute_get_period(self):
        for record in self:
            today = record.date
            period_ids = self.env['account.period'].search([('date_start','<=',today), ('date_stop','>=',today)], limit=1)
            record.period_id = period_ids

    period_id = fields.Many2one('account.period', 'Period', compute='_compute_get_period',store=True)
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Fiscal Year',
                                    related='period_id.fiscalyear_id', store=True)

    @api.onchange('date')
    def _onchange_date(self):
        '''On the form view, a change on the date will trigger onchange() on account.move
        but not on account.move.line even the date field is related to account.move.
        Then, trigger the _onchange_amount_currency manually.
        '''
        if self.date:
            period_id = self.env['account.period'].search([('date_start','<=',self.date), ('date_stop','>=',self.date)], limit=1)
            self.period_id = period_id.id
        self.line_ids._onchange_amount_currency()

    @api.multi
    @api.constrains('date', 'period_id')
    def check_period(self):
        for record in self:
            if record.period_id.state == 'done':
                raise UserError(_('You can not create journal entries in a closed period %s') % (record.period_id.name))

    @api.multi
    @api.constrains('fiscalyear_id')
    def check_fiscalyear(self):
        for record in self:
            if record.fiscalyear_id.state == 'done':
                raise UserError(_('%s is already closed') % (record.fiscalyear_id.name))

    @api.model
    def create(self, vals):
        context = dict(self._context or {})
        context['period_id'] = vals['period_id'] if 'period_id' in vals else self._compute_get_period()
        context['check_move_validity'] = False
        context['partner_id'] = vals.get('partner_id')
        move = super(AccountMove, self.with_context(context)).create(vals)
        move.assert_balanced()
        return move

    @api.multi
    def _centralise(self, mode):
        assert mode in ('debit', 'credit'), 'Invalid Mode' #to prevent sql injection
        account_move_line_obj = self.env['account.move.line']
        currency_obj = self.env['res.currency']
        context = self._context.copy()
        for move in self:
            if mode=='credit':
                account_id = move.journal_id.default_debit_account_id.id
                mode2 = 'debit'
                if not account_id:
                    raise UserError(
                            _('There is no default debit account defined \n' \
                                    'on journal "%s".') % move.journal_id.name)
            else:
                account_id = move.journal_id.default_credit_account_id.id
                mode2 = 'credit'
                if not account_id:
                    raise UserError(_('There is no default credit account defined \n' \
                                    'on journal "%s".') % move.journal_id.name)
    
            # find the first line of this move with the current mode
            # or create it if it doesn't exist
            self.env.cr.execute('select id from account_move_line where move_id=%s and centralisation=%s limit 1', (move.id, mode))
            res = self.env.cr.fetchone()
            if res:
                line_id = res[0]
            else:
                context.update({'journal_id': move.journal_id.id, 'period_id': move.period_id.id})
                line_id = account_move_line_obj.with_context(context).create({
                    'name': _(mode.capitalize()+' Centralisation'),
                    'centralisation': mode,
                    'partner_id': False,
                    'account_id': account_id,
                    'move_id': move.id,
                    'journal_id': move.journal_id.id,
                    'period_id': move.period_id.id,
                    'date': move.period_id.date_stop,
                    'debit': 0.0,
                    'credit': 0.0,
                })
                line_id = line_id.id
            # find the first line of this move with the other mode
            # so that we can exclude it from our calculation
            self.env.cr.execute('select id from account_move_line where move_id=%s and centralisation=%s limit 1', (move.id, mode2))
            res = self.env.cr.fetchone()
            if res:
                line_id2 = res[0]
            else:
                line_id2 = 0
    
            self.env.cr.execute('SELECT SUM(%s) FROM account_move_line WHERE move_id=%%s AND id!=%%s' % (mode,), (move.id, line_id2))
            result = self.env.cr.fetchone()[0] or 0.0
            if mode2 == 'credit':
                self.env.cr.execute('update account_move_line set credit=%s where id=%s', (result, line_id))
                self.invalidate_cache()
            else:
                self.env.cr.execute('update account_move_line set debit=%s where id=%s', (result, line_id))
                self.invalidate_cache()

            self.env.cr.execute("select currency_id, sum(amount_currency) as amount_currency from account_move_line where move_id = %s and currency_id is not null group by currency_id", (move.id,))
            currency_result = self.env.cr.dictfetchall()
            if currency_result:
                for row in currency_result:
                    currency_id = currency_obj.browse(row.get('currency_id'))
                    if not currency_id.is_zero(row.get('amount_currency')):
                        amount_currency = row.get('amount_currency') * -1
                        account_id = amount_currency > 0 and move.journal_id.default_debit_account_id.id or move.journal_id.default_credit_account_id.id
                        self.env.cr.execute('select id from account_move_line where move_id=%s and centralisation=\'currency\' and currency_id = %s limit 1', (move.id, row['currency_id']))
                        res = self.env.cr.fetchone()
                        if res:
                            self.env.cr.execute('update account_move_line set amount_currency=%s , account_id=%s where id=%s', (amount_currency, account_id, res[0]))
                            self.invalidate_cache()
                        else:
                            context.update({'journal_id': move.journal_id.id, 'period_id': move.period_id.id})
                            line_id = account_move_line_obj.create({
                                'name': _('Currency Adjustment'),
                                'centralisation': 'currency',
                                'partner_id': False,
                                'account_id': account_id,
                                'move_id': move.id,
                                'journal_id': move.journal_id.id,
                                'period_id': move.period_id.id,
                                'date': move.period_id.date_stop,
                                'debit': 0.0,
                                'credit': 0.0,
                                'currency_id': row['currency_id'],
                                'amount_currency': amount_currency,
                            })
        return True

    #
    # Validate a balanced move. If it is a centralised journal, create a move.
    #
    def validate(self):
        valid_moves = [] #Maintains a list of moves which can be responsible to create analytic entries
        obj_move_line = self.env['account.move.line']
        for move in self:
            journal = move.journal_id
            amount = 0
            line_ids = []
            line_draft_ids = []
            company_id = None
            # makes sure we don't use outdated period
            obj_move_line._update_journal_check(journal.id, move.period_id.id)
            for line in move.line_ids:
                amount += line.debit - line.credit
                line_ids.append(line.id)
                if line.state=='draft':
                    line_draft_ids.append(line.id)

                if not company_id:
                    company_id = line.account_id.company_id.id
                if not company_id == line.account_id.company_id.id:
                    raise UserError(_("Cannot create moves for different companies."))

                if line.account_id.currency_id and line.currency_id:
                    if line.account_id.currency_id.id != line.currency_id.id and (line.account_id.currency_id.id != line.account_id.company_id.currency_id.id):
                        raise UserError(_("""Couldn't create move with currency different from the secondary currency of the account "%s - %s". Clear the secondary currency field of the account definition if you want to accept all currencies.""") % (line.account_id.code, line.account_id.name))
            if abs(amount) < 10 ** -5:
                # If the move is balanced
                # Add to the list of valid moves
                # (analytic lines will be created later for valid moves)
                valid_moves.append(move.id)
                # Check whether the move lines are confirmed

                if not line_draft_ids:
                    continue
                # Update the move lines (set them as valid)
                move_line_ids = obj_move_line.browse(line_draft_ids)
                move_line_ids.write({'state': 'posted'})

                account = {}
                account2 = {}

                if journal.type in ('purchase','sale'):
                    for line in move.line_id:
                        code = amount = 0
                        key = (line.account_id.id, line.tax_code_id.id)
                        if key in account2:
                            code = account2[key][0]
                            amount = account2[key][1] * (line.debit + line.credit)
                        elif line.account_id.id in account:
                            code = account[line.account_id.id][0]
                            amount = account[line.account_id.id][1] * (line.debit + line.credit)
                        if (code or amount) and not (line.tax_code_id or line.tax_amount):
                            line.write({
                                'tax_code_id': code,
                                'tax_amount': amount
                            })
            elif journal.centralisation:
                # If the move is not balanced, it must be centralised...

                # Add to the list of valid moves
                # (analytic lines will be created later for valid moves)
                valid_moves.append(move.id)
                #
                # Update the move lines (set them as valid)
                #
                move._centralise('debit')
                move._centralise('credit')
                move_line_ids = obj_move_line.browse(line_draft_ids)
                move_line_ids.write({'state': 'posted'})
            else:
                # We can't validate it (it's unbalanced)
                # Setting the lines as draft
                not_draft_line_ids = list(set(line_ids) - set(line_draft_ids))
                if not_draft_line_ids:
                    draft_line_ids = obj_move_line.browse(not_draft_line_ids)
                    draft_line_ids.write({'state': 'posted'})
        # Create analytic lines for the valid moves
        valid_moves_ids = self.env['account.move'].browse(valid_moves)
        for move in valid_moves_ids:
            move.line_ids.create_analytic_lines()
        valid_moves = [move.id for move in valid_moves_ids]
        return len(valid_moves) > 0 and valid_moves or False

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _description = "Journal Items"

    state = fields.Selection([('draft', 'Unposted'), ('posted', 'Posted')], string='Status',
                             related='move_id.state', store=True, compute_sudo=True)
    period_id = fields.Many2one('account.period', string='Period', ondelete='restrict', readonly=True,
                                         related='move_id.period_id', store=True)
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Fiscal Year',related='period_id.fiscalyear_id', store=True)
    centralisation = fields.Selection([('normal','Normal'),('credit','Credit Centralisation'),('debit','Debit Centralisation'),('currency','Currency Adjustment')], 'Centralisation', default='normal')

    @api.multi
    def _update_journal_check(self, journal_id, period_id):
        journal_obj = self.env['account.journal']
        period_obj = self.env['account.period']
        jour_period_obj = self.env['account.journal.period']
        self.env.cr.execute('SELECT state FROM account_journal_period WHERE journal_id = %s AND period_id = %s', (journal_id, period_id))
        result = self.env.cr.fetchall()
        journal = journal_obj.browse(journal_id)
        period = period_obj.browse(period_id)
        for (state,) in result:
            if state == 'done':
                raise UserError(_('You can not add/modify entries in a closed period %s of journal %s.') % (period.name, journal.name))
        if not result:
            jour_period_obj.create({
                'name': (journal.code or journal.name)+':'+(period.name or ''),
                'journal_id': journal.id,
                'period_id': period.id
            })
        return True

    @api.model
    def _query_get(self, domain=None):
        self.check_access_rights('read')
        fiscalyear_obj = self.env['account.fiscalyear']
        context = dict(self._context or {})
        domain = domain or []
        if not isinstance(domain, (list, tuple)):
            domain = safe_eval(domain)

        date_field = 'date'
        if context.get('aged_balance'):
            date_field = 'date_maturity'
        if context.get('date_to'):
            domain += [(date_field, '<=', context['date_to'])]
        if context.get('date_from'):
            if not context.get('strict_range'):
                domain += ['|', (date_field, '>=', context['date_from']), ('account_id.user_type_id.include_initial_balance', '=', True)]
            elif context.get('initial_bal'):
                domain += [(date_field, '<', context['date_from'])]
            else:
                domain += [(date_field, '>=', context['date_from'])]

        if context.get('journal_ids'):
            domain += [('journal_id', 'in', context['journal_ids'])]

        state = context.get('state')
        if state and state.lower() != 'all':
            domain += [('move_id.state', '=', state)]

        if context.get('company_id'):
            domain += [('company_id', '=', context['company_id'])]

        if 'company_ids' in context:
            domain += [('company_id', 'in', context['company_ids'])]

        if context.get('reconcile_date'):
            domain += ['|', ('reconciled', '=', False), '|', ('matched_debit_ids.max_date', '>', context['reconcile_date']), ('matched_credit_ids.max_date', '>', context['reconcile_date'])]
 
        if context.get('account_tag_ids'):
            domain += [('account_id.tag_ids', 'in', context['account_tag_ids'].ids)]
 
        if context.get('account_ids'):
            domain += [('account_id', 'in', context['account_ids'].ids)]
 
        if context.get('analytic_tag_ids'):
            domain += [('analytic_tag_ids', 'in', context['analytic_tag_ids'].ids)]
 
        if context.get('analytic_account_ids'):
            domain += [('analytic_account_id', 'in', context['analytic_account_ids'].ids)]
 
        if context.get('partner_ids'):
            domain += [('partner_id', 'in', context['partner_ids'].ids)]
 
        if context.get('partner_categories'):
            domain += [('partner_id.category_id', 'in', context['partner_categories'].ids)]

        if not context.get('fiscalyear'):
            if context.get('all_fiscalyear'):
                #this option is needed by the aged balance report because otherwise, if we search only the draft ones, an open invoice of a closed fiscalyear won't be displayed
                fiscalyear_ids = fiscalyear_obj.search([])
                domain += [('fiscalyear_id', 'in', fiscalyear_ids.ids), ('move_id.state', '=', 'draft')]
            else:
                fiscalyear_ids = fiscalyear_obj.search([('state', '=', 'draft')])
                domain += [('fiscalyear_id', 'in', fiscalyear_ids.ids), ('move_id.state', '=', 'draft')]
        else:
            #for initial balance as well as for normal query, we check only the selected FY because the best practice is to generate the FY opening entries
            fiscalyear_ids = context.get('fiscalyear')
            domain += [('fiscalyear_id', 'in', fiscalyear_ids.ids), ('move_id.state', '=', 'draft')]

        where_clause = ""
        where_clause_params = []
        tables = ''
        if domain:
            query = self._where_calc(domain)
            # Wrap the query with 'company_id IN (...)' to avoid bypassing company access rights.
            self._apply_ir_rules(query)

            tables, where_clause, where_clause_params = query.get_sql()
        return tables, where_clause, where_clause_params


    def convert_to_period(self):
        context = dict(self._context or {})
        period_obj = self.env['account.period']
        #check if the period_id changed in the context from client side
        if context.get('period_id', False):
            period_id = context.get('period_id')
            if type(period_id) == str:
                period_ids = period_obj.search([('name', 'ilike', period_id)])
                context = dict(context, period_id=period_ids and period_ids[0] or False)
        return context

    @api.model
    def default_get(self, fields):
        context = dict(self._context or {})
        if not context.get('period_id', False):
            context['period_id'] = context.get('search_default_period_id', False)
        context = self.convert_to_period()
        rec = super(AccountMoveLine, self).default_get(fields)
        if 'line_ids' not in self._context:
            return rec

        #compute the default credit/debit of the next line in case of a manual entry
        balance = 0
        for line in self.move_id.resolve_2many_commands(
                'line_ids', self._context['line_ids'], fields=['credit', 'debit']):
            balance += line.get('debit', 0) - line.get('credit', 0)
        # if we are here, line_ids is in context, so journal_id should also be.
        currency = self._context.get('journal_id') and self.env["account.journal"].browse(self._context['journal_id']).company_id.currency_id
        if currency:
            balance = currency.round(balance)
        if balance < 0:
            rec.update({'debit': -balance})
        if balance > 0:
            rec.update({'credit': balance})
        return rec