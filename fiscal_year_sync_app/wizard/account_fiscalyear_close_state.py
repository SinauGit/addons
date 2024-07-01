# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountFiscalyearCloseState(models.TransientModel):
    """
    Closes  Account Fiscalyear
    """
    _name = "account.fiscalyear.close.state"
    _description = "Fiscalyear Close state"

    fy_id = fields.Many2one('account.fiscalyear', \
                                 'Fiscal Year to Close', required=True, help="Select a fiscal year to close")

    @api.multi
    def data_save(self):
        """
        This function close account fiscalyear
        """
        account_move_obj = self.env['account.move']

        for record in self:
            fy_id = record.fy_id.id
            account_move_ids = account_move_obj.search([('period_id.fiscalyear_id', '=', fy_id), ('state', '=', "draft")])
            if account_move_ids:
                raise UserError(_('In order to close a fiscalyear, you must first post related journal entries.'))

            self._cr.execute('UPDATE account_journal_period ' \
                        'SET state = %s ' \
                        'WHERE period_id IN (SELECT id FROM account_period \
                        WHERE fiscalyear_id = %s)',
                    ('done', fy_id))
            self._cr.execute('UPDATE account_period SET state = %s ' \
                    'WHERE fiscalyear_id = %s', ('done', fy_id))
            self._cr.execute('UPDATE account_fiscalyear ' \
                    'SET state = %s WHERE id = %s', ('done', fy_id))
            return {'type': 'ir.actions.act_window_close'}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
