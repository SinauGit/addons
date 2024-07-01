# -*- coding: utf-8 -*-
{
    "name" : "Fiscal Year for Accounting",
    "author": "Edge Technologies",
    "version" : "12.0.1.2",
    'live_test_url':'https://youtu.be/9yNdDJ6T0Xk',
    "images":['static/description/main_screenshot.png'],
    'summary': "Account fiscal year account fiscal period account fiscal year and period Accounting fiscal year Accounting fiscal period Accounting fiscal year and period manage fiscal year for accounting manage fiscal year for invoicing custom fiscal year accounting",
    "description": """
                App for creating opening journal entry for new fiscal year

                """,
    "license" : "OPL-1",
    "depends" : ['account'], #,'l10n_generic_coa'],
    "data": [
        'security/ir.model.access.csv',
        # 'data/account_demo.xml',
        'data/data_account_type.xml',
        'wizard/account_period_close_view.xml',
        'views/account_fiscalperiod_view.xml',
        'views/account_fiscalyear_view.xml',
        'views/account_view.xml',
        'wizard/account_fiscalyear_close_state.xml',
        'wizard/account_fiscalyear_close_view.xml',
        'wizard/account_open_closed_fiscalyear_view.xml',
    ],
    "auto_install": False,
    "price": 88,
    "currency": 'EUR',
    "installable": True,
    "category" : "Accounts",
    "post_init_hook": 'post_init_hook',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
