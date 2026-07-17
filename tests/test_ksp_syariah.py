from odoo.tests.common import TransactionCase

class TestKSPSyariah(TransactionCase):

    def setUp(self):
        super(TestKSPSyariah, self).setUp()
        self.Pembiayaan = self.env['ksp.pembiayaan.syariah']
        self.CreditScoring = self.env['ksp.credit.scoring']
        self.Partner = self.env['res.partner']
        
        # Create dummy partner
        self.anggota_test = self.Partner.create({
            'name': 'Test Anggota Syariah',
            'email': 'test@syariah.com',
            'property_account_receivable_id': self.env['account.account'].search([('account_type', '=', 'asset_receivable')], limit=1).id
        })

    def test_01_murabahah_calculation(self):
        """Test perhitungan margin pembiayaan Murabahah"""
        pembiayaan = self.Pembiayaan.create({
            'anggota_id': self.anggota_test.id,
            'akad': 'murabahah',
            'harga_beli': 10000000,
            'margin': 2000000,
            'tenor': 12
        })
        # Harga Jual harus sama dengan Harga Beli + Margin
        self.assertEqual(pembiayaan.harga_jual, 12000000, "Perhitungan Harga Jual Murabahah Salah")
        
    def test_02_credit_scoring_logic(self):
        """Test internal scoring dan approval matrix"""
        scoring = self.CreditScoring.create({
            'anggota_id': self.anggota_test.id,
            'poin_lama_anggota': 100,
            'poin_saldo_simpanan': 80,
            'poin_riwayat_npl': 90,
            'gunakan_slik': False # Matikan SLIK agar test murni internal
        })
        
        # Total skor harusnya: (100 * 0.2) + (80 * 0.3) + (90 * 0.5) = 20 + 24 + 45 = 89
        self.assertAlmostEqual(scoring.total_skor, 89.0, places=2, msg="Perhitungan total skor salah")
        self.assertEqual(scoring.rekomendasi, 'SETUJUI OTOMATIS', "Approval matrix logic salah untuk skor >= 80")

    def test_03_slik_api_mock(self):
        """Test perilaku SLIK API Mock"""
        scoring = self.CreditScoring.create({
            'anggota_id': self.anggota_test.id,
            'poin_lama_anggota': 100,
            'poin_saldo_simpanan': 100,
            'poin_riwayat_npl': 100,
            'gunakan_slik': True
        })
        
        # Tarik SLIK
        scoring.action_fetch_slik()
        
        self.assertEqual(scoring.slik_status, 'clear', "Mock SLIK gagal mengembalikan status clear")
        self.assertTrue(scoring.slik_outstanding_luar > 0, "Mock SLIK gagal mengembalikan baki debet")
        
        # Ubah status secara manual jadi danger untuk test auto-tolak
        scoring.slik_status = 'danger'
        self.assertEqual(scoring.rekomendasi, 'TOLAK (Terdapat Kredit Macet Eksternal)', "Sistem gagal menolak kredit bermasalah dari SLIK")
