{
    'name': 'Pendaftaran Siswa',
    'version': '12.0.1.0.0',
    'summary': 'Pendaftaran Siswa Sekolah',
    'description': """
        Modul yang berfungsi untuk mengatur pendaftaran peserta didik baru dan pindahan
    """,
    "category": "Education",
    'author': 'Muhammad Azis - 087881071515',
    'company': 'Ismata Nusantara Abadi',
    'website': "https://www.ismata.co.id",
    'depends': ['base_sekolah', 'website', 'sale', 'crm', 'calendar', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'report/report_print.xml',
        'report/report_action.xml',
        'views/view.xml',
        'views/templates.xml',
        'templates/pendaftaran_templates.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
