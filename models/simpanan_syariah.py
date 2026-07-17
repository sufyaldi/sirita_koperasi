from odoo import models, fields, api

class SimpananSyariah(models.Model):
    _name = 'ksp.simpanan.syariah'
    _description = 'Simpanan Syariah (BMT)'

    name = fields.Char(string='Nomor Referensi', required=True, copy=False, readonly=True, default='Baru')
    anggota_id = fields.Many2one('res.partner', string='Anggota', required=True)
    jenis_simpanan = fields.Selection([
        ('pokok', 'Simpanan Pokok'),
        ('wajib', 'Simpanan Wajib'),
        ('wadiah', 'Simpanan Sukarela (Wadi\'ah)')
    ], string='Jenis Simpanan', required=True, default='wadiah')
    
    saldo = fields.Monetary(string='Saldo Saat Ini', compute='_compute_saldo', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    
    @api.depends('anggota_id')
    def _compute_saldo(self):
        # Placeholder untuk logic menghitung mutasi
        for rec in self:
            rec.saldo = 0.0
