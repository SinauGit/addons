from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class CreateUserLogin(models.TransientModel):
    _name = 'partner.user.login'
    _description = 'Create Login From Partner'

    users_line = fields.One2many('users.line', 'user_login_id', string='User Line')

    @api.model
    def default_get(self, fields):
        res = super(CreateUserLogin, self).default_get(fields)
        vals = []
        for x in self.env['res.partner'].browse(self._context.get('active_ids')):
            if not x.email:
                raise UserError(('%s tidak memiliki email !' % x.name))
            vals.append((0,0, {'partner_id': x.id, 'login': x.email, 'password': 'sdcq'}))
        res['users_line'] = vals
        return res

    @api.multi
    def create_login(self):
        for o in self:
            vals = {}
            for i in o.users_line:
                vals = {
                    'partner_id': i.partner_id.id,
                    'login': i.login,
                    'password': i.password,
                    'company_id': self.env.ref('base.main_company').id,
                    'groups_id': [(6, 0, [
                                            self.env.ref('base_sekolah.group_sekolah_orangtua').id,
                                            self.env.ref('base.group_user').id
                    ])]
                }
                user_id = self.env['res.users'].create(vals)
                i.partner_id.user_id = user_id


class UserLoginLine(models.TransientModel):
    _name = 'users.line'

    user_login_id = fields.Many2one('partner.user.login', 'Partner User Login', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    login = fields.Char('Login', required=True)
    password = fields.Char('Password', default='sdcq', required=True)
    # groups_id = fields.Many2many('res.groups', column1='user_datas_id', column2="group_id", string='Groups', required=True)
