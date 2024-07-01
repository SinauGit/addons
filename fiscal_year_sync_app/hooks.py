# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID
from odoo import api


def post_init_hook(cr, registry):
    cr.execute("""
                update ir_model_data set noupdate=False where
                model ='account.account.type'""")
