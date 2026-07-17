from odoo import models, fields, api
import json

class CreditScoring(models.Model):
    _name = 'ksp.credit.scoring'
    _description = 'Internal Credit Scoring & SLIK OJK Mock'

    name = fields.Char(string='Nomor Scoring', required=True, copy=False, readonly=True, default='Baru')
    anggota_id = fields.Many2one('res.partner', string='Anggota', required=True)
    tanggal_skor = fields.Datetime(string='Waktu Penilaian', default=fields.Datetime.now)
    
    # Internal Scoring Variables
    poin_lama_anggota = fields.Integer(string='Poin Lama Keanggotaan')
    poin_saldo_simpanan = fields.Integer(string='Poin Saldo Simpanan')
    poin_riwayat_npl = fields.Integer(string='Poin Riwayat Pembayaran (Koperasi)')
    
    # SLIK OJK Data (Mock)
    gunakan_slik = fields.Boolean(string='Gunakan Data SLIK Eksternal?', default=True, help="Centang jika ingin menggunakan data SLIK OJK sebagai pertimbangan wajib.")
    slik_status = fields.Selection([
        ('not_checked', 'Belum Dicek'),
        ('clear', 'Clear (KOL 1)'),
        ('warning', 'Warning (KOL 2)'),
        ('danger', 'Danger (KOL 3-5)')
    ], string='Status iDeb SLIK', default='not_checked')
    slik_outstanding_luar = fields.Monetary(string='Total Outstanding Bank Lain')
    slik_raw_response = fields.Text(string='Raw Response API SLIK')
    
    total_skor = fields.Float(string='Skor Akhir (0-100)', compute='_compute_total_skor', store=True)
    rekomendasi = fields.Char(string='Rekomendasi Sistem', compute='_compute_rekomendasi')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    @api.depends('poin_lama_anggota', 'poin_saldo_simpanan', 'poin_riwayat_npl')
    def _compute_total_skor(self):
        for rec in self:
            # Simple weighting: 20% lama, 30% saldo, 50% riwayat
            rec.total_skor = (rec.poin_lama_anggota * 0.2) + (rec.poin_saldo_simpanan * 0.3) + (rec.poin_riwayat_npl * 0.5)

    @api.depends('total_skor', 'slik_status', 'gunakan_slik')
    def _compute_rekomendasi(self):
        for rec in self:
            # Jika fitur SLIK digunakan dan statusnya Danger, langsung tolak
            if rec.gunakan_slik and rec.slik_status == 'danger':
                rec.rekomendasi = 'TOLAK (Terdapat Kredit Macet Eksternal)'
            elif rec.total_skor >= 80:
                rec.rekomendasi = 'SETUJUI OTOMATIS'
            elif rec.total_skor >= 50:
                rec.rekomendasi = 'REVIEW MANAJER'
            else:
                rec.rekomendasi = 'TOLAK (Skor Terlalu Rendah)'

    def action_fetch_slik(self):
        """ Mockup hit API ke biro kredit swasta/OJK """
        for rec in self:
            # Simulasi respon API
            mock_response = {
                'nik': rec.anggota_id.vat or '0000',
                'kolektibilitas_terburuk': 1,
                'total_plafon': 50000000,
                'total_baki_debet': 15000000
            }
            rec.slik_raw_response = json.dumps(mock_response, indent=4)
            rec.slik_status = 'clear'
            rec.slik_outstanding_luar = mock_response['total_baki_debet']
