{
    'name': 'Kesiswaan',
    'version': '12.0.1.0.0',
    'summary': """Kesiswaan Sekolah""",
    'description': 'Ini merupakan module di bidang kesiswaan',
    "category": "Education",
    'author': 'RizkyAbdiSyahputraHasibuan-085175257741',
    'company': 'PT LINTANG UTAMA INFOTEK',
    'website': "https://lui.co.id/",
    'depends': ['base', 'base_sekolah',],
    'data': [
        'security/ir.model.access.csv',     # File hak akses
        'views/prestasi_siswa_views.xml',   # File yang mendefinisikan views dan menuitem
    ],
    'images': [],
    'license': 'AGPL-3',
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
