from odoo import models, fields, api

class BaitulMaal(models.Model):
    _name = 'ksp.baitul.maal'
    _description = 'Penerimaan Zakat, Infaq, Sadaqah (ZIS)'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nomor Transaksi', required=True, copy=False, readonly=True, default='Baru')
    tipe_dana = fields.Selection([
        ('zakat', 'Zakat'),
        ('infaq', 'Infaq / Sadaqah'),
        ('wakaf', 'Wakaf Tunai')
    ], string='Tipe Dana ZIS', required=True, default='infaq', tracking=True)
    
    donatur_id = fields.Many2one('res.partner', string='Donatur/Muzakki', help="Kosongkan jika Hamba Allah")
    nama_hamba_allah = fields.Char(string='Nama (Jika Bukan Anggota)')
    
    tanggal = fields.Date(string='Tanggal Penerimaan', default=fields.Date.context_today, required=True, tracking=True)
    nominal = fields.Monetary(string='Nominal', required=True, tracking=True)
    keterangan = fields.Text(string='Keterangan')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Diterima & Dibukukan')
    ], string='Status', default='draft', tracking=True)
    
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Baru') == 'Baru':
                vals['name'] = self.env['ir.sequence'].next_by_code('ksp.baitul.maal') or 'ZIS-NEW'
        return super(BaitulMaal, self).create(vals_list)

    def action_terima_dana(self):
        for rec in self:
            journal = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
            if not journal:
                raise ValueError("Tidak ditemukan Jurnal Bank.")
                
            account_bank = journal.default_account_id
            if not account_bank:
                account_bank = self.env['account.account'].search([('account_type', 'in', ['asset_cash', 'asset_current'])], limit=1)
                
            # Akun penampungan ZIS (Liabilitas / Titipan)
            account_zis = self.env['account.account'].search([('account_type', 'in', ['liability_current', 'liability_payable'])], limit=1)
            
            if not account_bank or not account_zis:
                rec.state = 'done'
                rec.message_post(body="Dana diterima, namun Jurnal gagal dibuat karena konfigurasi akun belum lengkap.")
                return
                
            move_vals = {
                'move_type': 'entry',
                'journal_id': journal.id,
                'date': rec.tanggal,
                'ref': f"Penerimaan {dict(self._fields['tipe_dana'].selection).get(rec.tipe_dana)} - {rec.name}",
                'line_ids': [
                    (0, 0, {
                        'name': f'Kas/Bank (Penerimaan {rec.tipe_dana})',
                        'debit': rec.nominal,
                        'credit': 0.0,
                        'account_id': account_bank.id
                    }),
                    (0, 0, {
                        'name': f'Dana Titipan {rec.tipe_dana.capitalize()}',
                        'debit': 0.0,
                        'credit': rec.nominal,
                        'account_id': account_zis.id
                    }),
                ]
            }
            
            move = self.env['account.move'].create(move_vals)
            rec.message_post(body=f"Dana ZIS berhasil dibukukan. Jurnal: {move.name}")
            rec.state = 'done'
