{
    'name': 'Notulensi',
    'version': '12.0.1.0.0',
    'summary': """Modul Untuk Notulensi""",
    'description': 'Ini merupakan module Notulensi',
    "category": "Education",
    'author': 'RizkyAbdiSyahputraHasibuan-085175257741',
    'company': 'PT LINTANG UTAMA INFOTEK',
    'website': "https://lui.co.id/",
    'depends': [ 'base', 'project', 'sale_timesheet',],
    'data': [
        'security/ir.model.access.csv',     # File hak akses
        'views/notulensi_view.xml',   # File yang mendefinisikan views dan menuitem
    ],
    'images': [],
    'license': 'AGPL-3',
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}