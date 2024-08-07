{
    'name': 'Security',
    'version': '12.0.1.0.0',
    'summary': """Keperluan Untuk Security""",
    'description': 'Ini merupakan module Security',
    "category": "Education",
    'author': 'RizkyAbdiSyahputraHasibuan-085175257741',
    'company': 'PT LINTANG UTAMA INFOTEK',
    'website': "https://lui.co.id/",
    'depends': ['base', 'base_sekolah', 'hr_holidays',],
    'data': [
        'security/ir.model.access.csv',     # File hak akses
        'security/security.xml',
        'views/surat_kepegawaian_view.xml',   # File yang mendefinisikan views dan menuitem
    ],
    'images': [],
    'license': 'AGPL-3',
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
