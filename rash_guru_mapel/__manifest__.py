{
    'name': 'Guru Mapel',
    'version': '12.0.1.0.0',
    'summary': """Modul Guru Mata Pelajaran""",
    'description': 'Ini merupakan module Guru Mata Pelajaran',
    "category": "Education",
    'author': 'RizkyAbdiSyahputraHasibuan-085175257741',
    'company': 'PT LINTANG UTAMA INFOTEK',
    'website': "https://lui.co.id/",
    'depends': ['aa_kurikulum','base_sekolah','base', ],
    'data': [
        'security/ir.model.access.csv',     # File hak akses
        'views/guru_mapel_view.xml',   # File yang mendefinisikan views dan menuitem
    ],
    'images': [],
    'license': 'AGPL-3',
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
