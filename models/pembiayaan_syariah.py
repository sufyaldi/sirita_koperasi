from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class PembiayaanSyariah(models.Model):
    _name = 'ksp.pembiayaan.syariah'
    _description = 'Pembiayaan Syariah (BMT)'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nomor Referensi', required=True, copy=False, readonly=True, default='Baru')
    anggota_id = fields.Many2one('res.partner', string='Anggota', required=True, domain=[('is_company', '=', False)])
    akad = fields.Selection([
        ('murabahah', 'Murabahah (Jual Beli)'),
        ('mudharabah', 'Mudharabah (Bagi Hasil)'),
        ('musyarakah', 'Musyarakah (Kongsi)')
    ], string='Jenis Akad', required=True, default='murabahah')
    
    # Nilai Pembiayaan
    harga_beli = fields.Monetary(string='Harga Beli (Pokok)', required=True)
    margin = fields.Monetary(string='Margin Keuntungan', help='Hanya untuk Murabahah')
    nisbah_bmt = fields.Float(string='Nisbah BMT (%)', help='Hanya untuk Mudharabah/Musyarakah')
    nisbah_anggota = fields.Float(string='Nisbah Anggota (%)')
    harga_jual = fields.Monetary(string='Harga Jual (Total)', compute='_compute_harga_jual', store=True)
    
    tenor = fields.Integer(string='Tenor (Bulan)', required=True, default=12)
    tanggal_pengajuan = fields.Date(string='Tanggal Pengajuan', default=fields.Date.context_today)
    
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    state = fields.Selection([
        ('draft', 'Pengajuan'),
        ('scoring', 'Credit Scoring & SLIK'),
        ('approved', 'Disetujui'),
        ('active', 'Berjalan'),
        ('done', 'Lunas'),
        ('rejected', 'Ditolak')
    ], string='Status', default='draft', track_visibility='onchange')

    # Relasi ke SLIK / Scoring
    scoring_id = fields.Many2one('ksp.credit.scoring', string='Hasil Scoring')
    skor_akhir = fields.Float(related='scoring_id.total_skor', string='Skor Kredit')
    
    @api.depends('harga_beli', 'margin', 'akad')
    def _compute_harga_jual(self):
        for rec in self:
            if rec.akad == 'murabahah':
                rec.harga_jual = rec.harga_beli + rec.margin
            else:
                rec.harga_jual = rec.harga_beli

    def action_request_scoring(self):
        self.state = 'scoring'

    def action_approve(self):
        self.state = 'approved'

    def action_disburse(self):
        for rec in self:
            journal = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
            if not journal:
                # Fallback to general journal if no bank journal exists
                journal = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
                
            account_receivable = rec.anggota_id.property_account_receivable_id
            account_bank = journal.default_account_id
            if not account_bank:
                account_bank = self.env['account.account'].search([('account_type', 'in', ['asset_cash', 'asset_current'])], limit=1)
            account_margin = self.env['account.account'].search([('account_type', 'in', ['liability_current', 'liability_payable'])], limit=1)
            
            if not (account_receivable and account_bank and account_margin):
                # Fallback just change state if accounts are not properly configured
                rec.state = 'active'
                return
                
            move_vals = {
                'move_type': 'entry',
                'journal_id': journal.id,
                'date': fields.Date.context_today(self),
                'ref': f"Pencairan {rec.name} - {rec.anggota_id.name}",
                'line_ids': [
                    (0, 0, {
                        'name': 'Piutang Murabahah',
                        'debit': rec.harga_jual,
                        'credit': 0.0,
                        'partner_id': rec.anggota_id.id,
                        'account_id': account_receivable.id
                    }),
                    (0, 0, {
                        'name': 'Pencairan Pokok (Kas/Bank)',
                        'debit': 0.0,
                        'credit': rec.harga_beli,
                        'partner_id': rec.anggota_id.id,
                        'account_id': account_bank.id
                    }),
                    (0, 0, {
                        'name': 'Margin Ditangguhkan',
                        'debit': 0.0,
                        'credit': rec.margin,
                        'partner_id': rec.anggota_id.id,
                        'account_id': account_margin.id
                    }),
                ]
            }
            
            # Create journal entry
            move = self.env['account.move'].create(move_vals)
            # Link to chatter
            rec.message_post(body=f"Pencairan dana telah dilakukan. Jurnal dibuat: {move.name}")
            rec.state = 'active'

    def action_pay_installment(self):
        """Simulasi pembayaran cicilan 1 bulan dan amortisasi margin (PSAK 106)"""
        for rec in self:
            if rec.state != 'active':
                continue
                
            journal = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
            if not journal:
                raise ValueError("Tidak ditemukan Jurnal Bank untuk pembayaran.")
                
            # Asumsi cicilan flat (proporsional per bulan)
            cicilan_pokok = rec.harga_beli / rec.tenor
            cicilan_margin = rec.margin / rec.tenor
            total_cicilan = cicilan_pokok + cicilan_margin
            
            account_receivable = rec.anggota_id.property_account_receivable_id
            account_bank = journal.default_account_id
            account_margin_ditangguhkan = self.env['account.account'].search([('account_type', 'in', ['liability_current', 'liability_payable'])], limit=1)
            account_pendapatan_margin = self.env['account.account'].search([('account_type', 'in', ['income', 'income_other'])], limit=1)
            
            if not (account_receivable and account_bank and account_margin_ditangguhkan and account_pendapatan_margin):
                rec.message_post(body="Gagal memproses cicilan: Konfigurasi akun (Bank/Piutang/Pendapatan) belum lengkap.")
                return
                
            move_vals = {
                'move_type': 'entry',
                'journal_id': journal.id,
                'date': fields.Date.context_today(self),
                'ref': f"Pembayaran Cicilan {rec.name}",
                'line_ids': [
                    # 1. Penerimaan Uang Cicilan
                    (0, 0, {
                        'name': 'Kas/Bank (Penerimaan Cicilan)',
                        'debit': total_cicilan,
                        'credit': 0.0,
                        'partner_id': rec.anggota_id.id,
                        'account_id': account_bank.id
                    }),
                    (0, 0, {
                        'name': 'Piutang Murabahah (Pelunasan)',
                        'debit': 0.0,
                        'credit': total_cicilan,
                        'partner_id': rec.anggota_id.id,
                        'account_id': account_receivable.id
                    }),
                    # 2. Amortisasi Margin Ditangguhkan -> Pendapatan Margin (PSAK 106)
                    (0, 0, {
                        'name': 'Amortisasi Margin Ditangguhkan',
                        'debit': cicilan_margin,
                        'credit': 0.0,
                        'partner_id': rec.anggota_id.id,
                        'account_id': account_margin_ditangguhkan.id
                    }),
                    (0, 0, {
                        'name': 'Pendapatan Margin Murabahah',
                        'debit': 0.0,
                        'credit': cicilan_margin,
                        'partner_id': rec.anggota_id.id,
                        'account_id': account_pendapatan_margin.id
                    }),
                ]
            }
            
            move = self.env['account.move'].create(move_vals)
            rec.message_post(body=f"Pembayaran cicilan bulan ini berhasil. Pendapatan margin diakui. Jurnal: {move.name}")
