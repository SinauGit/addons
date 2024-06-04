# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.osv import expression

class AccountFiscalyear(models.Model):
    _name = "account.fiscalyear"
    _description = "Fiscal Year"
    _order = 'date_start, id'

    name = fields.Char('Fiscal Year', required=True)
    code = fields.Char('Code', size=6, required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.user.company_id)
    date_start = fields.Date('Start Date', required=True)
    date_stop = fields.Date('End Date', required=True)
    period_ids = fields.One2many('account.period', 'fiscalyear_id', 'Periods')
    state = fields.Selection([('draft','Open'), ('done','Closed')], 'Status', readonly=True, copy=False, default='draft')
    end_journal_period_id = fields.Many2one('account.journal.period', 'End of Year Entries Journal', readonly=True, copy=False)

    @api.constrains('date_start', 'date_stop')
    def _check_duration(self):
        for x in self:
            if x.date_stop < x.date_start:
                msg = _('The start date of a fiscal year must precede its end date.')    
                raise UserError(msg) 
            return

    @api.multi
    def create_period3(self, interval=3):
        interval = 3
        period_obj = self.env['account.period']
        for fy in self:
            ds = datetime.strptime(str(fy.date_start), '%Y-%m-%d').date()
            period_obj.create({
                    'name':  "%s %s" % (_('Opening Period'), ds.strftime('%Y')),
                    'code': ds.strftime('00/%Y'),
                    'date_start': ds,
                    'date_stop': ds,
                    'special': True,
                    'fiscalyear_id': fy.id,
                })
            while ds.strftime('%Y-%m-%d') < str(fy.date_stop):
                de = ds + relativedelta(months=interval, days=-1)
                if de.strftime('%Y-%m-%d') > str(fy.date_stop):
                    de = datetime.strptime(str(fy.date_stop), '%Y-%m-%d')

                period_obj.create({
                    'name': ds.strftime('%m/%Y'),
                    'code': ds.strftime('%m/%Y'),
                    'date_start': ds.strftime('%Y-%m-%d'),
                    'date_stop': de.strftime('%Y-%m-%d'),
                    'fiscalyear_id': fy.id,
                })
                ds = ds + relativedelta(months=interval)
        return


    @api.multi
    def create_period(self, interval=1):
        interval = 1
        period_obj = self.env['account.period']
        for fy in self:
            ds = datetime.strptime(str(fy.date_start), '%Y-%m-%d').date()
            period_obj.create({
                    'name':  "%s %s" % (_('Opening Period'), ds.strftime('%Y')),
                    'code': ds.strftime('00/%Y'),
                    'date_start': ds,
                    'date_stop': ds,
                    'special': True,
                    'fiscalyear_id': fy.id,
                })
            while ds.strftime('%Y-%m-%d') < str(fy.date_stop):
                de = ds + relativedelta(months=interval, days=-1)
                if de.strftime('%Y-%m-%d') > str(fy.date_stop):
                    de = datetime.strptime(str(fy.date_stop), '%Y-%m-%d')

                period_obj.create({
                    'name': ds.strftime('%m/%Y'),
                    'code': ds.strftime('%m/%Y'),
                    'date_start': ds.strftime('%Y-%m-%d'),
                    'date_stop': de.strftime('%Y-%m-%d'),
                    'fiscalyear_id': fy.id,
                })
                ds = ds + relativedelta(months=interval)
        return

class AccountPeriod(models.Model):
    _name = "account.period"
    _description = "Account period"

    name = fields.Char('Period Name', required=True)
    code = fields.Char('Code', size=12)
    special = fields.Boolean('Opening/Closing Period',help="These periods can overlap.")
    date_start = fields.Date('Start of Period', required=True, states={'done':[('readonly',True)]})
    date_stop = fields.Date('End of Period', required=True, states={'done':[('readonly',True)]})
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Fiscal Year', required=True, states={'done':[('readonly',True)]})
    state = fields.Selection([('draft','Open'), ('done','Closed')], 'Status', readonly=True, copy=False, default='draft')
    company_id = fields.Many2one('res.company', string='Company', store=True, readonly=True, default=lambda self: self.env.user.company_id )

    _sql_constraints = [
        ('name_only_uniq', 'unique(name, company_id)', 'The name of the period must be unique per company!'),
    ]

    @api.returns('self')
    def find(self, dt=None):
        context = (self._context or {})
        if not dt:
            dt = fields.Date.context_today(self)
        args = [('date_start', '<=' ,dt), ('date_stop', '>=', dt)]
        if context.get('company_id', False):
            args.append(('company_id', '=', context['company_id']))
        else:
            company_id = self.env.user.company_id.id
            args.append(('company_id', '=', company_id))
        result = []
        if context.get('account_period_prefer_normal', True):
            # look for non-special periods first, and fallback to all if no result is found
            result = self.search(args + [('special', '=', False)])
        if not result:
            result = self.search(args)
        if not result:
            action = self.env.ref('fiscal_year_sync_app.action_account_period')
            msg = _('There is no period defined for this date: %s.\nPlease go to Configuration/Periods.')
            raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))
        return result

    @api.constrains('date_stop')
    def _check_duration(self):
        for obj_period in self:
            if obj_period.date_stop < obj_period.date_start:
                msg = _('The duration of the Period(s) is/are invalid.')    
                raise UserError(msg)
        return 

    @api.constrains('date_stop')
    def _check_year_limit(self):
        for obj_period in self:
            if obj_period.special:
                continue
            if obj_period.fiscalyear_id.date_stop < obj_period.date_stop or \
                obj_period.fiscalyear_id.date_stop < obj_period.date_start or \
                obj_period.fiscalyear_id.date_start > obj_period.date_start or \
                obj_period.fiscalyear_id.date_start > obj_period.date_stop:
                    msg = ('The period is invalid. Either some periods are overlapping or the period\'s dates are not matching the scope of the fiscal year.')
                    raise UserError(msg)
            pids = self.search([('date_stop','>=',obj_period.date_start),('date_start','<=',obj_period.date_stop),('special','=',False),('id','<>',obj_period.id)])
            for period in pids:
                if period.fiscalyear_id.company_id.id==obj_period.fiscalyear_id.company_id.id:
                    msg = ('The period is invalid. Either some periods are overlapping or the period\'s dates are not matching the scope of the fiscal year.')
                    raise UserError(msg) 
        return True

    @api.multi
    def action_draft(self):
        mode = 'draft'
        for period in self:
            if period.fiscalyear_id.state == 'done':
                raise UserError(_('You can not re-open a period which belongs to closed fiscal year'))
        self._cr.execute('update account_journal_period set state=%s where period_id in %s', (mode, tuple(self.ids),))
        self._cr.execute('update account_period set state=%s where id in %s', (mode, tuple(self.ids),))
        return True

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        domain = args or []
        domain = expression.AND([domain, ['|', ('name', operator, name), ('code', operator, name)]])
        rec = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(rec).name_get()

    @api.multi
    def write(self, vals):
        if 'company_id' in vals:
            move_lines = self.env['account.move.line'].search([('period_id', 'in', self.ids)])
            if move_lines:
                raise UserError(_('This journal already contains items for this period, therefore you cannot modify its company field.'))
        return super(AccountPeriod, self).write(vals)


class AccountJournalPeriod(models.Model):
    _name = "account.journal.period"
    _description = "Journal Period"
    _order = "period_id"

    name = fields.Char('Journal-Period Name', required=True)
    journal_id = fields.Many2one('account.journal', 'Journal', required=True, ondelete="cascade")
    period_id = fields.Many2one('account.period', 'Period', required=True, ondelete="cascade")
    active = fields.Boolean('Active', help="If the active field is set to False, it will allow you to hide the journal period without removing it.")
    state =fields.Selection([('draft','Draft'), 
                             ('printed','Printed'), 
                             ('done','Done')], 'Status', required=True, readonly=True,
                            help='When journal period is created. The status is \'Draft\'. If a report is printed it comes to \'Printed\' status. When all transactions are done, it comes in \'Done\' status.')
    fiscalyear_id = fields.Many2one('account.fiscalyear','Fiscal Year')
    company_id = fields.Many2one('res.company', string='Company', store=True, readonly=True, default=lambda self: self.env.user.company_id )

    @api.multi
    def _check(self):
        for obj in self:
            self._cr.execute('select * from account_move_line where journal_id=%s and period_id=%s limit 1', (obj.journal_id.id, obj.period_id.id))
            res = self._cr.fetchall()
            if res:
                raise UserError(_('You cannot modify/delete a journal with entries for this period.'))
        return True

    @api.multi
    def write(self, vals):
        for period in self:
            period._check()
        return super(AccountJournalPeriod, self).write(vals)

    @api.model
    def create(self, vals):
        period_id = vals.get('period_id',False)
        if period_id:
            period = self.env['account.period'].browse(period_id)
            vals['state']=period.state
        return super(AccountJournalPeriod, self).create(vals)

    @api.multi
    def unlink(self):
        for period in self:
            period._check()
        return super(AccountJournalPeriod, self).unlink()


