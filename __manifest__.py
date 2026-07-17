{
    'name': 'KSP Syariah',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Ekstensi Syariah (BMT), Credit Scoring, SLIK OJK, dan Laporan Kemenkop',
    'description': """
        Modul ini memperluas fungsionalitas KSP standar menjadi:
        - Dukungan Koperasi Syariah (BMT) dengan akad Murabahah & Wadi'ah.
        - Internal Credit Scoring & Mockup API SLIK OJK.
        - Laporan Tingkat Kesehatan Koperasi (CAR, NPF, FDR, ROA, ROE) sesuai standar Kemenkop/OJK.
    """,
    'author': 'Sufyaldy, TIPD IAIN Parepare',
    'depends': ['base', 'account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/pembiayaan_views.xml',
        'views/simpanan_views.xml',
        'views/credit_scoring_views.xml',
        'views/rasio_kesehatan_views.xml',
        'views/baitul_maal_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
