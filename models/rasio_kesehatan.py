from odoo import models, fields, api

class RasioKesehatan(models.TransientModel):
    _name = 'ksp.rasio.kesehatan'
    _description = 'Wizard Laporan Rasio Kesehatan Koperasi (Kemenkop)'

    tanggal_laporan = fields.Date(string='Tanggal Laporan', default=fields.Date.context_today)
    
    # Hasil Rasio
    car = fields.Float(string='CAR (Capital Adequacy Ratio) %', compute='_compute_rasio')
    npf = fields.Float(string='NPF (Non-Performing Financing) %', compute='_compute_rasio')
    fdr = fields.Float(string='FDR (Financing to Deposit Ratio) %', compute='_compute_rasio')
    roa = fields.Float(string='ROA (Return on Asset) %', compute='_compute_rasio')
    roe = fields.Float(string='ROE (Return on Equity) %', compute='_compute_rasio')

    def _compute_rasio(self):
        # Placeholder untuk kalkulasi riil dari CoA Odoo
        # Secara riil, ini akan query ke account.move.line berdasarkan tipe akun
        for rec in self:
            rec.car = 20.5   # Dummy
            rec.npf = 3.2    # Dummy, Sehat < 5%
            rec.fdr = 85.0   # Dummy
            rec.roa = 2.1    # Dummy
            rec.roe = 15.0   # Dummy

    def action_generate_excel(self):
        import base64
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Tanggal Laporan', 'CAR (%)', 'NPF (%)', 'FDR (%)', 'ROA (%)', 'ROE (%)'])
        
        for rec in self:
            writer.writerow([
                rec.tanggal_laporan,
                rec.car,
                rec.npf,
                rec.fdr,
                rec.roa,
                rec.roe
            ])
        
        csv_data = output.getvalue()
        output.close()
        
        attachment = self.env['ir.attachment'].create({
            'name': 'Laporan_Rasio_Kesehatan.csv',
            'type': 'binary',
            'datas': base64.b64encode(csv_data.encode('utf-8')),
            'mimetype': 'text/csv'
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'new',
        }
