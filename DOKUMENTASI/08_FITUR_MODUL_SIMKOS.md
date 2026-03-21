# 📦 08 — Fitur & Modul SIMKOS — Penjelasan Sangat Detail

## Daftar Semua Modul SIMKOS

Project ini terdiri dari **16+ modul** yang saling terhubung untuk mengelola bisnis kost/kontrakan. Berikut penjelasan detail setiap modul: apa fungsinya, halaman-halamannya, model database yang digunakan, dan bagaimana modul tersebut terhubung dengan modul lain.

---

## 1. Dashboard (`apps/dashboard/`)

**URL:** `/` (halaman utama setelah login)

**Fungsi:** Menampilkan **ringkasan statistik bisnis kost** dalam satu halaman. Pemilik kost bisa melihat kondisi bisnis secara cepat tanpa harus buka-buka modul lain.

**Komponen:**
| Widget | Data yang Ditampilkan | Sumber Data (Model) |
|--------|----------------------|---------------------|
| Card Total Properti | Jumlah properti kost aktif | `Properti.objects.filter(aktif=True).count()` |
| Card Penyewa Aktif | Jumlah penyewa aktif | `Penyewa.objects.filter(status='aktif').count()` |
| Card Kontrak Aktif | Jumlah kontrak sewa berjalan | `KontrakSewa.objects.filter(status='aktif').count()` |
| Card Tagihan Pending | Jumlah tagihan belum dibayar | `TagihanSewa.objects.filter(status='belum_bayar').count()` |
| Card Pemasukan Bulan Ini | Total pembayaran sewa bulan ini | `PembayaranSewa` sum bulan berjalan |
| Card Pengeluaran Bulan Ini | Total biaya operasional bulan ini | `TransaksiBiaya` sum bulan berjalan |
| Tingkat Hunian | Persentase kamar terisi | `Kamar` terisi vs total |
| Chart Area Pemasukan & Pengeluaran | Tren 6 bulan terakhir | Pembayaran & Biaya per bulan |
| Donut Status Kamar | Distribusi: Tersedia, Terisi, Perbaikan | `Kamar` grouped by status |
| Donut Status Tagihan | Distribusi: Lunas, Belum Bayar, Sebagian, Terlambat | `TagihanSewa` grouped by status |
| Tabel Tagihan Belum Bayar | Daftar tagihan menunggak | `TagihanSewa.objects.filter(status='belum_bayar')` |

**Kenapa Dashboard penting?**
Tanpa dashboard, untuk mengetahui "berapa pemasukan bulan ini?", harus buka Laporan → filter tanggal → hitung manual. Dengan dashboard, jawabannya **langsung terlihat** saat login.

---

## 2. Properti (`apps/properti/`)

**URL:** `/properti/`

**Fungsi:** Mengelola **data properti kost/kontrakan** — unit bisnis utama dari SIMKOS. Semua modul lain (kamar, sewa, tagihan) mereferensikan data properti.

### Model yang Digunakan:

```python
Properti   → Data properti (nama, alamat, tipe: kost/kontrakan/apartemen/rumah sewa)
TipeKamar  → Tipe kamar dan harganya (AC, Non-AC, VIP, Studio) + fasilitas
Kamar      → Detail setiap kamar (nomor, lantai, status: tersedia/terisi/perbaikan)
```

### Halaman dan URL:
| URL | View | Fungsi | Permission |
|-----|------|--------|------------|
| `/properti/` | PropertiListView | Daftar semua properti | properti.daftar_properti.read |
| `/properti/tambah/` | PropertiCreateView | Form tambah properti baru | properti.daftar_properti.create |
| `/properti/<id>/` | PropertiDetailView | Detail properti + denah kamar | properti.daftar_properti.read |
| `/properti/<id>/edit/` | PropertiUpdateView | Edit data properti | properti.daftar_properti.write |
| `/properti/tipe-kamar/` | TipeKamarListView | Daftar tipe kamar | properti.tipe_kamar.read |
| `/properti/tipe-kamar/add/` | TipeKamarCreateView | Tambah tipe kamar | properti.tipe_kamar.create |
| `/properti/kamar/` | KamarListView | Daftar semua kamar | properti.kamar.read |
| `/properti/kamar/add/` | KamarCreateView | Tambah kamar | properti.kamar.create |

### Fitur Khusus:
- **Denah Interaktif:** Detail properti menampilkan denah kamar drag-and-drop yang menunjukkan posisi, status, penghuni, dan harga setiap kamar
- **Property `total_kamar`:** Menghitung total kamar di properti
- **Property `kamar_tersedia` / `kamar_terisi`:** Status real-time ketersediaan kamar
- **Upload Foto Properti:** Disimpan di `media/properti/`
- **Tipe Properti:** Kost, Kontrakan, Apartemen, Rumah Sewa

### Koneksi ke Modul Lain:
```
Properti ──→ Kamar (setiap properti punya banyak kamar)
Kamar    ──→ KontrakSewa (kamar disewakan via kontrak)
TipeKamar ──→ Kamar (menentukan harga dan fasilitas kamar)
```

---

## 3. Penyewa (`apps/penyewa/`)

**URL:** `/penyewa/`

**Fungsi:** Mengelola **data penyewa kost/kontrakan** — orang yang menghuni kamar.

### Model:

```python
Penyewa → Data lengkap penghuni (nama, NIK, jenis kelamin, telepon, email,
          alamat asal, pekerjaan, foto KTP, foto, kontak darurat, status)
```

### Halaman dan URL:
| URL | View | Fungsi |
|-----|------|--------|
| `/penyewa/` | PenyewaListView | Daftar semua penyewa |
| `/penyewa/tambah/` | PenyewaCreateView | Form tambah penyewa baru |
| `/penyewa/<id>/` | PenyewaDetailView | Detail penyewa + riwayat kontrak |
| `/penyewa/<id>/edit/` | PenyewaUpdateView | Edit data penyewa |

### Fitur Khusus:
- **Upload Foto KTP:** Untuk verifikasi identitas penyewa
- **Kontak Darurat:** Nama, telepon, hubungan — penting untuk keadaan darurat
- **Status:** Aktif, Nonaktif, Blacklist
- **Riwayat Kontrak:** Melihat semua kontrak sewa penyewa (aktif dan selesai)

### Koneksi ke Modul Lain:
```
Penyewa ──→ KontrakSewa (penyewa membuat kontrak untuk menghuni kamar)
Penyewa ──→ TagihanSewa (tagihan dikirim ke penyewa via kontrak)
Penyewa ──→ PembayaranSewa (penyewa melakukan pembayaran tagihan)
```

---

## 4. Sewa / Kontrak (`apps/sewa/`)

**URL:** `/sewa/`

**Fungsi:** Inti dari bisnis kost — mengelola **kontrak sewa, tagihan bulanan, dan pembayaran** dari penyewa.

### Model yang Digunakan:

```python
KontrakSewa    → Kontrak antara penyewa dan kamar
                 (nomor kontrak, tanggal mulai/selesai, harga sewa, deposit, status)
                 Nomor auto-generate: KTR/2026/02/0001

TagihanSewa    → Tagihan sewa bulanan
                 (kontrak, periode bulan/tahun, jumlah, jatuh tempo, status bayar)
                 Nomor auto-generate: TGH/2026/02/0001

PembayaranSewa → Record pembayaran dari penyewa
                 (tagihan, jumlah bayar, tanggal, metode: tunai/transfer/ewallet/qris, bukti)
                 Nomor auto-generate: BYR/2026/02/0001
```

### Halaman dan URL:
| URL | View | Fungsi |
|-----|------|--------|
| `/sewa/kontrak/` | KontrakListView | Daftar kontrak sewa |
| `/sewa/kontrak/add/` | KontrakCreateView | Buat kontrak baru |
| `/sewa/kontrak/<id>/` | KontrakDetailView | Detail kontrak + tagihan |
| `/sewa/tagihan/` | TagihanListView | Daftar semua tagihan |
| `/sewa/tagihan/add/` | TagihanCreateView | Buat tagihan baru |
| `/sewa/pembayaran/` | PembayaranListView | Daftar pembayaran |
| `/sewa/pembayaran/add/` | PembayaranCreateView | Input pembayaran |

### Alur Bisnis Kost:
```
┌─────────┐     ┌───────────┐     ┌──────────┐     ┌───────────┐
│ KONTRAK │ ──► │  TAGIHAN  │ ──► │PEMBAYARAN│ ──► │   LUNAS   │
│  SEWA   │     │  BULANAN  │     │  SEWA    │     │           │
│         │     │           │     │          │     │ Status    │
│ Penyewa │     │ Generate  │     │ Penyewa  │     │ tagihan   │
│ ↔ Kamar │     │ per bulan │     │ bayar    │     │ = Lunas   │
│         │     │           │     │ (bukti)  │     │           │
└─────────┘     └───────────┘     └──────────┘     └───────────┘
```

### Bagaimana Auto-Generate Nomor Bekerja:

```python
# Contoh untuk KontrakSewa:
1. Ambil kontrak terakhir bulan ini: KTR/2026/02/0003
2. Extract nomor urut: 0003
3. Increment: 0004
4. Return: KTR/2026/02/0004

# Sama untuk TagihanSewa (TGH/...) dan PembayaranSewa (BYR/...)
```

### Fitur Pembayaran:
- **Metode Pembayaran:** Tunai, Transfer Bank, E-Wallet, QRIS
- **Bukti Pembayaran:** Upload foto/screenshot bukti transfer
- **Auto-Update Status:** Setelah pembayaran, status tagihan otomatis berubah:
  - Jumlah bayar = jumlah tagihan → Status = "Lunas"
  - Jumlah bayar < jumlah tagihan → Status = "Bayar Sebagian"
- **Sisa Tagihan:** Otomatis menghitung sisa yang belum dibayar

---

## 5. Biaya Operasional (`apps/biaya/`)

**URL:** `/biaya/`

**Fungsi:** Pencatatan **pengeluaran operasional kost** — listrik, air, internet, perbaikan, gaji karyawan, dll.

### Model:

```python
KategoriBiaya  → Kategori pengeluaran (Listrik, Air, Internet, Perbaikan, Gaji, dll)
TransaksiBiaya → Setiap transaksi pengeluaran
                 (nomor, kategori, jumlah, tanggal, keterangan, properti)
                 Nomor auto-generate: EXP/2026/02/0001
```

### Halaman dan URL:
| URL | View | Fungsi |
|-----|------|--------|
| `/biaya/` | BiayaListView | Daftar transaksi biaya |
| `/biaya/tambah/` | BiayaCreateView | Input biaya baru |
| `/biaya/<id>/edit/` | BiayaUpdateView | Edit transaksi |
| `/biaya/kategori/` | KategoriBiayaListView | Daftar kategori biaya |
| `/biaya/kategori/add/` | KategoriBiayaCreateView | Tambah kategori |

### Contoh Pengeluaran Kost:
```
┌─────────────────────────────────────────────┐
│ Transaksi Biaya Operasional KOS             │
├──────────────┬────────────┬─────────────────┤
│ Kategori     │ Jumlah     │ Keterangan      │
├──────────────┼────────────┼─────────────────┤
│ Listrik      │ Rp 2.500.000 │ PLN bulan Feb │
│ Air PDAM     │ Rp 800.000   │ PDAM bulan Feb │
│ Internet     │ Rp 500.000   │ WiFi bulanan  │
│ Perbaikan    │ Rp 350.000   │ Pipa kamar 103 │
│ Gaji         │ Rp 2.000.000 │ Gaji karyawan │
│ Kebersihan   │ Rp 300.000   │ Bahan cleaning │
└──────────────┴────────────┴─────────────────┘
```

---

## 6. Laporan (`apps/laporan/`)

**URL:** `/laporan/`

**Fungsi:** Menghasilkan **laporan analisis bisnis kost** — pemasukan, pengeluaran, hunian, dan keuangan keseluruhan.

### Jenis Laporan:

| Laporan | URL | Data | Sumber |
|---------|-----|------|--------|
| Laporan Pemasukan | `/laporan/pemasukan/` | Riwayat pembayaran sewa, filter tanggal & penyewa | `PembayaranSewa` |
| Laporan Pengeluaran | `/laporan/pengeluaran/` | Riwayat biaya operasional, filter kategori | `TransaksiBiaya` |
| Laporan Hunian | `/laporan/hunian/` | Statistik kamar per properti, tingkat hunian | `Properti`, `Kamar`, `KontrakSewa` |
| Laporan Keuangan | `/laporan/keuangan/` | Ringkasan: pemasukan - pengeluaran = laba bersih | `PembayaranSewa`, `TransaksiBiaya` |

### Chart di Halaman Laporan:
- **Donut Chart (Distribusi Kamar):** Tersedia vs Terisi di Laporan Hunian
- **Bar Chart (Pemasukan vs Pengeluaran):** Komposisi keuangan
- Support **dark mode dan light mode** sepenuhnya

### Filter Data:
- **Tanggal:** Filter berdasarkan rentang tanggal (Flatpickr)
- **Penyewa:** Filter pemasukan per penyewa
- **Kategori:** Filter pengeluaran per kategori biaya

---

## 7. AI Assistant (`apps/ai_assistant/`)

**URL:** `/ai/`

**Fungsi:** **Asisten AI** untuk analisis bisnis kost yang terintegrasi dengan data real-time SIMKOS.

### Halaman:
| URL | Fungsi |
|-----|--------|
| `/ai/` | Dashboard AI — ringkasan cerdas bisnis |
| `/ai/chat/` | Chat AI — tanya jawab dengan asisten AI |
| `/ai/settings/` | Pengaturan AI — API key, model, preferensi |

### Dashboard AI Analytics:
- **Skor Kesehatan Bisnis:** Metrik otomatis berdasarkan hunian, pembayaran, pengeluaran
- **Tren Pendapatan Sewa 6 Bulan:** Bar chart data pemasukan
- **Distribusi Status Kamar:** Donut chart status kamar
- **Rekomendasi AI:** Saran otomatis berdasarkan data kos

### Chat AI:
- Tanya jawab menggunakan bahasa natural
- Terintegrasi dengan data kos real-time
- Contoh pertanyaan: "Berapa tingkat hunian bulan ini?", "Siapa penyewa paling lama?"

---

## 8. HR / Karyawan KOS (`apps/hr/`)

**URL:** `/hr/`

**Fungsi:** Mengelola **data karyawan kost** — penjaga, cleaning service, tukang, pengelola.

### Halaman:
| URL | Fungsi | Model |
|-----|--------|-------|
| `/hr/karyawan/` | Daftar karyawan | Karyawan |
| `/hr/karyawan/add/` | Tambah karyawan baru | Karyawan |
| `/hr/karyawan/<id>/edit/` | Edit data karyawan | Karyawan |
| `/hr/karyawan/<id>/` | Detail karyawan | Karyawan |
| `/hr/departemen/` | Daftar departemen | Departemen |
| `/hr/jabatan/` | Daftar jabatan | Jabatan |
| `/hr/absensi/` | Rekap absensi | Absensi |
| `/hr/absensi/create/` | Input absensi harian | Absensi |
| `/hr/penggajian/` | Daftar penggajian | Penggajian |
| `/hr/penggajian/create/` | Buat slip gaji | Penggajian |

### Contoh Jabatan di Kost:
- Pengelola Kost
- Penjaga / Satpam
- Cleaning Service
- Tukang / Maintenance

---

## 9. Automation / Telegram Bot (`apps/automation/`)

**URL:** `/automation/`

**Fungsi:** Integrasi **Telegram Bot** untuk notifikasi otomatis event bisnis kost.

### Notifikasi yang Dikirim:
```
📅 Tagihan Baru
   TGH/2026/02/0042 — Kamar 101
   Penyewa: Budi Santoso
   Jumlah: Rp 1.500.000
   Jatuh Tempo: 10 Maret 2026

⚠️ Tagihan Terlambat
   Kamar 205 — Ahmad Fauzi
   Sudah 7 hari lewat jatuh tempo
   Sisa: Rp 1.200.000

💰 Pembayaran Diterima
   BYR/2026/02/0015 — Kamar 103
   Transfer BCA — Rp 1.500.000 (LUNAS)
```

---

## 10. User Management (`apps/user_management/`)

**URL:** `/users/`

**Fungsi:** Administrasi **akun pengguna** sistem SIMKOS.

### Halaman:
| URL | Fungsi |
|-----|--------|
| `/users/` | Daftar semua user |
| `/users/create/` | Buat akun user baru |
| `/users/<id>/edit/` | Edit user (nama, email, role) |
| `/users/<id>/` | Detail user (profil + aktivitas) |

### Fitur Khusus:
- **Assign Role:** Setiap user di-assign ke Role (Admin, Operator, Pengelola, dll)
- **Nonaktifkan Akun:** Set `is_active = False` → user tidak bisa login
- **Ganti Password:** Admin bisa reset password user lain

---

## 11. Permission Management (`apps/permission_management/`)

**URL:** `/access/`

**Fungsi:** UI visual untuk mengatur **hak akses RBAC** (Role-Based Access Control).

### Cara Kerja Permission:
```
┌──────────────────────────────────────────────────────┐
│ Edit Role: "Operator Kost"                            │
│                                                        │
│ Modul          │ Read │ Create │ Edit │ Delete │       │
│ ───────────────┼──────┼────────┼──────┼────────│       │
│ Properti       │  ☑   │   ☐    │  ☐   │   ☐   │       │
│  └ Kamar       │  ☑   │   ☐    │  ☐   │   ☐   │       │
│ Penyewa        │  ☑   │   ☑    │  ☑   │   ☐   │       │
│ Sewa/Kontrak   │  ☑   │   ☑    │  ☑   │   ☐   │       │
│ Tagihan        │  ☑   │   ☑    │  ☑   │   ☐   │       │
│ Pembayaran     │  ☑   │   ☑    │  ☑   │   ☐   │       │
│ Biaya          │  ☑   │   ☐    │  ☐   │   ☐   │       │
│ Laporan        │  ☑   │   ☐    │  ☐   │   ☐   │       │
│ ...            │      │        │      │        │       │
└──────────────────────────────────────────────────────┘

Hasil:
- Operator Kost BISA: lihat properti, kelola penyewa & sewa, input pembayaran
- Operator Kost TIDAK BISA: tambah/hapus properti, kelola biaya, hapus data
```

---

## 12. Pengaturan (`apps/pengaturan/`)

**URL:** `/pengaturan/`

**Fungsi:** Konfigurasi **sistem dan profil** kost.

### Halaman:
| URL | Fungsi | Model |
|-----|--------|-------|
| `/pengaturan/profil/` | Edit profil user login | User, Profile |
| `/pengaturan/perusahaan/` | Data perusahaan/kost | PengaturanPerusahaan |

### Data Perusahaan (Muncul di SEMUA halaman):
```python
{{ system_title }}          # "SIMKOS" atau "Kost Melati Indah"
{{ system_logo_url }}       # "/media/pengaturan/logo.png"
{{ system_favicon_url }}    # "/media/pengaturan/favicon.ico"
{{ company_address }}       # "Jl. Merpati No. 15, Bandung"
{{ company_phone }}         # "022-1234-5678"
```

---

## 13. Activity Log (`apps/activity_log/`)

**URL:** `/activity-log/`

**Fungsi:** Sistem **audit trail** — mencatat SEMUA aktivitas user secara otomatis.

### Data yang Dicatat:
| Field | Contoh |
|-------|--------|
| `user` | admin |
| `action` | CREATE |
| `model_name` | KontrakSewa |
| `object_repr` | "KTR/2026/02/0001 - Budi Santoso" |
| `changes` | `{"harga_sewa": ["1500000", "1600000"]}` |
| `ip_address` | 192.168.1.100 |
| `timestamp` | 2026-03-03 10:00:00 |

---

## Diagram Koneksi Antar Modul — Detail

```
                     ┌──────────────────────┐
                     │      DASHBOARD       │
                     │  (ringkasan kost)    │
                     └──────────┬───────────┘
                                │ query semua modul
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
    ┌───────────┐       ┌──────────────┐      ┌──────────────┐
    │ PROPERTI  │       │    SEWA      │      │   LAPORAN    │
    │ (kamar,   │◄──────│ (kontrak,    │      │ (analisa)    │
    │  tipe)    │       │  tagihan,    │      └──────────────┘
    └─────┬─────┘       │  bayar)      │             ▲
          │             └──────┬───────┘             │
          │                    │                     │
     ┌────┴────┐          ┌────┴─────┐              │
     ▼         ▼          ▼          ▼              │
 ┌────────┐┌────────┐┌────────┐┌──────────┐        │
 │PENYEWA ││TAGIHAN ││BAYAR   ││  BIAYA   │────────┘
 │ (data  ││ (sewa  ││(record ││ (operasi │
 │ pengh- ││ bulanan││ bayar) ││  onal)   │
 │  uni)  ││ )      ││        ││          │
 └────────┘└────────┘└────────┘└──────────┘
       │         │        │
       └─────────┼────────┘
                 ▼
    ┌─────────────────────────┐
    │   MODUL PENDUKUNG       │
    │                         │
    │ ┌────────────────────┐  │
    │ │ AI ASSISTANT       │  │ ← analisis data AI + chat
    │ └────────────────────┘  │
    │ ┌────────────────────┐  │
    │ │ ACTIVITY LOG       │  │ ← catat SEMUA aksi (otomatis)
    │ └────────────────────┘  │
    │ ┌────────────────────┐  │
    │ │ PENGATURAN         │  │ ← konfigurasi kost
    │ └────────────────────┘  │
    │ ┌────────────────────┐  │
    │ │ USER + PERMISSION  │  │ ← kelola akun & hak akses
    │ └────────────────────┘  │
    │ ┌────────────────────┐  │
    │ │ HR / KARYAWAN KOS  │  │ ← karyawan, absensi, gaji
    │ └────────────────────┘  │
    │ ┌────────────────────┐  │
    │ │ AUTOMATION         │  │ ← notifikasi Telegram
    │ └────────────────────┘  │
    └─────────────────────────┘
```

---

## Tabel Alur Keuangan Kost

| Event | Arus Kas | Contoh |
|-------|----------|--------|
| Kontrak Baru | – | Penyewa baru masuk Kamar 101 → kontrak dibuat |
| Tagihan Dibuat | – | TGH/2026/03/0001 — Rp 1.500.000 jatuh tempo 10 Maret |
| Penyewa Bayar | **+ Pemasukan** | BYR/2026/03/0001 — Transfer BCA Rp 1.500.000 |
| Bayar Listrik | **- Pengeluaran** | EXP/2026/03/0005 — PLN bulan Maret Rp 2.500.000 |
| Bayar Gaji | **- Pengeluaran** | EXP/2026/03/0010 — Gaji karyawan Rp 2.000.000 |
| Perbaikan | **- Pengeluaran** | EXP/2026/03/0012 — Pipa bocor Kamar 103 Rp 350.000 |

### Rumus Laba Bersih:
```
Laba Bersih = Total Pemasukan (Pembayaran Sewa) - Total Pengeluaran (Biaya Operasional)
Margin (%)  = (Laba Bersih / Total Pemasukan) × 100
```

---

## Dependency Map — Modul Mana Bergantung ke Mana?

```
┌─────────────────────────────────────────────────────────────┐
│                   MODULE DEPENDENCY MAP                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  LEVEL 0 (Foundation — tanpa dependency):                   │
│    ┌──────────┐  ┌────────────┐  ┌────────────────┐        │
│    │ PENGATURAN│  │ CORE       │  │ ACTIVITY LOG   │        │
│    │           │  │ (template  │  │ (standalone)   │        │
│    │           │  │  tags,     │  │                │        │
│    │           │  │  perms)    │  │                │        │
│    └──────────┘  └────────────┘  └────────────────┘        │
│                                                              │
│  LEVEL 1 (Depends on Foundation):                           │
│    ┌──────────┐  ┌────────────┐  ┌──────────┐              │
│    │ PROPERTI │  │ USER MGMT  │  │ PENYEWA  │              │
│    │ (kamar,  │  │ + PERM MGMT│  │          │              │
│    │  tipe)   │  └────────────┘  └──────────┘              │
│    └──────────┘                                              │
│                                                              │
│  LEVEL 2 (Depends on Properti + Penyewa):                   │
│    ┌──────────┐  ┌────────────┐                             │
│    │   SEWA   │  │   BIAYA    │                             │
│    │ (kontrak,│  │ (operasi-  │                             │
│    │  tagihan,│  │  onal)     │                             │
│    │  bayar)  │  │            │                             │
│    └──────────┘  └────────────┘                             │
│                                                              │
│  LEVEL 3 (Depends on multiple):                             │
│    ┌──────────┐  ┌────────────┐  ┌──────────┐              │
│    │ LAPORAN  │  │ DASHBOARD  │  │    AI    │              │
│    │(hunian,  │  │(statistik  │  │ASSISTANT │              │
│    │ keuangan)│  │ semua)     │  │          │              │
│    └──────────┘  └────────────┘  └──────────┘              │
│                                                              │
│  INDEPENDENT (Tidak bergantung ke modul lain):              │
│    ┌──────────┐  ┌────────────┐                             │
│    │   HR     │  │ AUTOMATION │                             │
│    │(karyawan)│  │ (Telegram) │                             │
│    └──────────┘  └────────────┘                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

*Lanjut ke [09_TIPS_DAN_BEST_PRACTICE.md](09_TIPS_DAN_BEST_PRACTICE.md) →*

*Dokumentasi perbaikan UI/UX terbaru: [16_PERBAIKAN_DAN_PENINGKATAN.md](16_PERBAIKAN_DAN_PENINGKATAN.md)*
