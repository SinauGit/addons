# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountPeriodClose(models.TransientModel):
    _name = "account.period.close"
    _description = "period close"

    sure = fields.Boolean('Check this box')

    @api.multi
    def data_save(self):
        account_move_obj = self.env['account.move']
        mode = 'done'
        active_ids = self._context.get('active_ids')
        period_ids = self.env['account.period'].browse(active_ids)
        for record in self:
            if record.sure:
                for period_id in period_ids:
                    account_move_ids = account_move_obj.search([('period_id', '=', period_id.id), ('state', '=', "draft")])
                    if account_move_ids:
                        raise UserError(_('In order to close a period, you must first post related journal entries.'))
                    self._cr.execute('update account_journal_period set state=%s where period_id=%s', (mode, period_id.id))
                    self._cr.execute('update account_period set state=%s where id=%s', (mode, period_id.id))
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
