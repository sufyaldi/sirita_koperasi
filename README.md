# KSP Syariah (BMT, Credit Scoring, SLIK OJK, & Laporan Kemenkop)

Modul Odoo ini dirancang untuk memperluas fungsionalitas Koperasi Simpan Pinjam (KSP) standar dengan mendukung operasional Koperasi Syariah (BMT), penilaian kelayakan kredit (Credit Scoring & SLIK OJK), serta pelaporan kesehatan koperasi sesuai standar Kementerian Koperasi dan UKM (Kemenkop) / OJK.

## 🚀 Fitur Utama

- **Dukungan Koperasi Syariah (BMT)**:
  - Implementasi Akad **Murabahah** (jual beli dengan margin keuntungan).
  - Implementasi Akad **Wadi'ah** (titipan murni).
- **Internal Credit Scoring & Mockup API SLIK OJK**:
  - Penilaian kelayakan pembiayaan anggota berdasarkan kriteria internal.
  - Simulasi/mockup integrasi API dengan SLIK OJK untuk mengecek riwayat kredit.
- **Laporan Tingkat Kesehatan Koperasi**:
  - Rasio Keuangan standar Kemenkop & OJK:
    - **CAR** (Capital Adequacy Ratio)
    - **NPF** (Non-Performing Financing)
    - **FDR** (Financing to Deposit Ratio)
    - **ROA** (Return on Assets)
    - **ROE** (Return on Equity)
- **Baitul Maal**:
  - Pengelolaan dana sosial (Zakat, Infaq, Sedekah, dan Wakaf - ZISWAF) secara terintegrasi.

## 📁 Struktur Direktori

```bash
tipd_koperasi/
├── models/             # Logika bisnis & relasi database Odoo
├── views/              # Tampilan Antarmuka (XML)
├── security/           # Hak akses pengguna (CSV)
├── tests/              # Automated unit testing
├── __init__.py
├── __manifest__.py     # Metadata manifest Odoo
└── README.md
```

## 🛠️ Persyaratan & Instalasi

### Dependensi Modul
Modul ini bergantung pada modul bawaan Odoo berikut:
- `base`
- `account`
- `mail`

### Langkah Instalasi
1. Salin folder `tipd_koperasi` ke dalam direktori `addons` Odoo Anda.
2. Aktifkan Mode Pengembang (Developer Mode) pada Odoo.
3. Masuk ke menu **Apps** dan klik **Update Apps List**.
4. Cari `KSP Syariah` atau `tipd_koperasi`.
5. Klik **Install**.

## 📝 Lisensi
Modul ini dirilis di bawah lisensi **AGPL-3**.

---
**Author**: Sufyaldy, TIPD IAIN Parepare
