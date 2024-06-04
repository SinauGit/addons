# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountOpenClosedFiscalyear(models.TransientModel):
    _name = "account.open.closed.fiscalyear"
    _description = "Choose Fiscal Year"

    fyear_id = fields.Many2one('account.fiscalyear', \
                                 'Fiscal Year', required=True, 
                                 help='Select Fiscal Year which you want to remove entries for its End of year entries journal')

    @api.multi
    def remove_entries(self):
        for record in self:
            move_obj = self.env['account.move']
            period_journal = record.fyear_id.end_journal_period_id or False
            if not period_journal:
                raise UserError(_("You have to set the 'End  of Year Entries Journal' for this Fiscal Year which is set after generating opening entries from 'Generate Opening Entries'."))
            if period_journal.period_id.state == 'done':
                raise UserError(_("You can not cancel closing entries if the 'End of Year Entries Journal' period is closed."))
            ids_move = move_obj.search([('journal_id','=',period_journal.journal_id.id),('period_id','=',period_journal.period_id.id)])
            if ids_move:
                self._cr.execute('delete from account_move where id IN %s', (tuple(ids_move.ids),))
        return {'type': 'ir.actions.act_window_close'}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
