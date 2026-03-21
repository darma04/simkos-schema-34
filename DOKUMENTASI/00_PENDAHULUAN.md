# 📘 00 — Pendahuluan: Mengenal Sistem SIMKOS dari NOL

## DAFTAR ISI
- [A. Apa itu SIMKOS?](#a-apa-itu-simkos)
- [B. Asal-Usul Project: Materialize / Sneat Starter Kit](#b-asal-usul-project)
- [C. Teknologi yang Digunakan (dan KENAPA)](#c-teknologi-yang-digunakan)
- [D. Persiapan & Instalasi dari Awal](#d-persiapan--instalasi)
- [E. Cara Menjalankan Project](#e-cara-menjalankan-project)
- [F. Arsitektur & Alur Kerja Django](#f-arsitektur--alur-kerja-django)
- [G. Peta Modul SIMKOS](#g-peta-modul-simkos)

---

## A. Apa itu SIMKOS?

**SIMKOS (Sistem Manajemen Kost)** = sistem informasi terintegrasi yang mengelola SEMUA proses bisnis rumah kost / kontrakan dalam SATU platform.

### Tanpa SIMKOS vs Dengan SIMKOS:
```
TANPA SIMKOS:                                DENGAN SIMKOS:
┌─────────────┐                              ┌───────────────────────────┐
│ Properti:   │  ← tidak sinkron →           │                           │
│ Catatan     │                              │    SATU SISTEM TERPADU    │
├─────────────┤                              │                           │
│ Penyewa:    │  ← data beda →               │   Properti ↔ Kamar       │
│ Buku tulis  │                              │   Penyewa ↔ Kontrak      │
├─────────────┤                              │   Tagihan ↔ Pembayaran   │
│ Keuangan:   │  ← salah hitung →            │   Biaya ↔ Laporan        │
│ Kalkulator  │                              │                           │
└─────────────┘                              │  Semua TERHUBUNG otomatis │
Hasil: Data tidak akurat,                    └───────────────────────────┘
       duplikasi, lambat                     Hasil: Real-time, akurat, efisien
```

### Modul SIMKOS yang Kita Bangun:
| No | Modul | Fungsi | Contoh Penggunaan |
|----|-------|--------|-------------------|
| 1 | Dashboard | Ringkasan bisnis kost real-time | Total properti, penyewa aktif, pemasukan bulan ini |
| 2 | Properti | Kelola data properti kost/kontrakan | Tambah properti "Kost Melati Indah" |
| 3 | Tipe Kamar | Tipe kamar dan harga | AC, Non-AC, VIP dengan harga masing-masing |
| 4 | Kamar | Data setiap kamar di properti | Kamar 101, Lantai 1, Status: Tersedia |
| 5 | Penyewa | Data penyewa kost | Nama, NIK, KTP, kontak darurat |
| 6 | Kontrak Sewa | Kontrak antara penyewa dan kamar | KTR/2026/02/0001 — Kamar 101, 12 bulan |
| 7 | Tagihan | Tagihan sewa bulanan | TGH/2026/02/0001 — Rp 1.500.000 |
| 8 | Pembayaran | Catatan pembayaran dari penyewa | BYR/2026/02/0001 — Transfer BCA |
| 9 | Biaya | Pengeluaran operasional | Listrik, air, perbaikan, gaji karyawan |
| 10 | Laporan | Analisis bisnis kost | Laporan Hunian, Keuangan, Pemasukan |
| 11 | HR / Karyawan KOS | Manajemen karyawan kost | Data karyawan, absensi, penggajian |
| 12 | AI Assistant | Asisten AI untuk analisis bisnis | Chat AI, Dashboard AI, rekomendasi |
| 13 | User Management | Kelola user sistem | Tambah user, atur role |
| 14 | Permission/RBAC | Hak akses berbasis role | Admin bisa semua, Operator hanya input |
| 15 | Pengaturan | Konfigurasi perusahaan | Logo, nama, alamat kost |
| 16 | Automation | Notifikasi otomatis | Kirim alert tagihan ke Telegram |

---

## B. Asal-Usul Project: Materialize / Sneat Starter Kit

### Latar Belakang

Project SIMKOS ini dibangun di atas **Materialize Bootstrap 5 Admin Template** dari **Pixinvent** — sebuah template admin dashboard premium.

```
Pixinvent membuat 2 versi:
┌─────────────────────────────────────────────────┐
│  1. FULL VERSION (berbayar premium)             │
│     - Semua halaman demo sudah jadi             │
│     - Charts, forms, tables, apps lengkap       │
│     - Ratusan file template                     │
│                                                 │
│  2. STARTER KIT (versi dasar) ← KITA PAKAI INI │
│     - Template KOSONG siap diisi                │
│     - Layout system (master, vertical, blank)   │
│     - Sidebar, navbar, footer sudah ada         │
│     - Theme engine (dark/light, RTL, colors)    │
│     - TIDAK ada halaman konten apapun           │
└─────────────────────────────────────────────────┘

Kenapa kita pilih STARTER KIT?
→ Karena kita MEMBANGUN SENDIRI semua fitur dari nol!
→ Full version = contoh demo, BUKAN aplikasi jadi
→ Starter kit = fondasi yang benar untuk custom app
```

### Apa yang Sudah Ada dari Starter Kit (Bawaan Pixinvent):

| Komponen | File | Fungsi |
|----------|------|--------|
| Master Layout | `templates/layout/master.html` | Template induk (DOCTYPE, head, body) |
| Layout Vertical | `templates/layout/layout_vertical.html` | Layout sidebar kiri |
| Layout Horizontal | `templates/layout/layout_horizontal.html` | Layout menu atas |
| Layout Blank | `templates/layout/layout_blank.html` | Layout tanpa menu (login) |
| Sidebar Menu | `templates/layout/partials/menu/` | Komponen sidebar |
| Navbar | `templates/layout/partials/navbar/` | Komponen navigation bar |
| Footer | `templates/layout/partials/footer/` | Komponen footer |
| Styles Partial | `templates/layout/partials/styles.html` | CSS global |
| Scripts Partial | `templates/layout/partials/scripts.html` | JS global |
| Theme Engine | `web_project/template_helpers/theme.py` | Class TemplateHelper |
| Layout Engine | `web_project/__init__.py` | Class TemplateLayout |
| Config | `config/template.py` | TEMPLATE_CONFIG (pengaturan tema) |
| Static Assets | `static/` | CSS, JS, fonts, icons vendor |

### Apa yang KITA Bangun Sendiri (Dari NOL):

| Komponen | File/Folder | Jumlah |
|----------|-------------|--------|
| Apps Django | `apps/` | 16+ modul (properti, penyewa, sewa, dll) |
| Models | `apps/*/models.py` | 15+ model database |
| Views | `apps/*/views.py` | 60+ view class (CBV) |
| Forms | `apps/*/forms.py` | 15+ form class |
| URLs | `apps/*/urls.py` | 16 file routing |
| Templates HTML | `templates/*/` | 60+ template halaman |
| Permission System | `apps/core/` | RBAC lengkap + caching |
| Auth System | `auth/` | Login, register, forgot password (Bahasa Indonesia) |
| JavaScript Logic | Di dalam template | Export PDF/Excel, AJAX delete, Chart.js |
| Dashboard Charts | `templates/dashboard/` | Grafik pemasukan, hunian, dll |
| AI Assistant | `apps/ai_assistant/` | Chat AI, Dashboard Analytics, Settings |
| Dokumentasi | `DOKUMENTASI/` | 18 file markdown penjelasan lengkap |

### Evolusi Project:

```
TAHAP 1: Starter Kit (Bawaan Pixinvent)
├── Layout system sudah jadi
├── Theme engine (dark/light mode)
├── Static assets (Bootstrap 5, jQuery, icons)
└── KOSONG — tidak ada halaman/fitur apapun

    ↓ (Kita kembangkan dengan bertahap)

TAHAP 2: Fondasi Django
├── Setup config/settings.py
├── Buat apps/ dengan 16+ modul SIMKOS
├── Buat models.py (Properti, Kamar, Penyewa, Sewa, dll)
├── Buat views.py (CBV untuk CRUD)
└── Konfigurasi URL routing

    ↓

TAHAP 3: Template & UI
├── Buat 60+ template HTML
├── Integrasi Materialize component (card, table, modal)
├── DataTables untuk semua list view
├── Export Excel & PDF
└── AJAX delete + toast notification

    ↓

TAHAP 4: Sistem Lanjutan
├── RBAC (Role-Based Access Control) lengkap
├── Dashboard dengan grafik Chart.js & ApexCharts
├── Denah Interaktif Kamar (drag & drop)
├── Laporan Hunian, Keuangan, Pemasukan, Pengeluaran
├── HR / Karyawan KOS Management
├── Automation (Telegram notification)
└── AI Assistant (Chat, Dashboard Analytics)

    ↓

TAHAP 5: Optimasi & Polish (Terbaru)
├── AI Dashboard Analytics (skor kesehatan bisnis, tren pendapatan)
├── AI Chat dengan integrasi data kos
├── Dark/Light mode support di semua chart
├── Mobile responsive layout (2-column cards)
├── Chart.js integrasi untuk bar chart pill-shaped
├── Export Excel/PDF standarisasi
└── Dokumentasi 18 file markdown
```

---

## C. Teknologi yang Digunakan (dan KENAPA)

### Backend — Django (Python)

```python
# Django = web framework Python tingkat tinggi
# Versi yang digunakan: Django 5.x

# KENAPA Django?
# 1. "Batteries included" — ORM, auth, admin, forms SUDAH ADA
# 2. Python — bahasa paling mudah dipelajari
# 3. Keamanan — CSRF, XSS, SQL injection protection OTOMATIS
# 4. Django Admin — panel admin gratis
# 5. Community — dokumentasi lengkap, banyak library
```

### Frontend — Materialize Bootstrap 5

```
Materialize Bootstrap 5 Admin Template (oleh Pixinvent)
├── Bootstrap 5     → Framework CSS responsif
├── jQuery           → Library JavaScript (DOM manipulation)
├── Popper.js        → Library untuk dropdown/tooltip positioning
├── Perfect Scrollbar → Scrollbar custom yang elegan
├── Node Waves       → Efek ripple saat klik (efek material design)
├── Hammer.js        → Touch gesture support (mobile)
├── TypeaheadJS      → Autocomplete search di navbar
├── Remix Icon       → 2000+ icon gratis (ri-* class)
├── Inter Font       → Google Font utama (modern, readable)
└── Template Customizer → Toggle dark/light, sidebar style
```

### Library Tambahan (Kita Pasang Sendiri):

```
DataTables           → Tabel interaktif (search, sort, pagination)
pdfMake              → Generate PDF di browser (client-side)
Chart.js             → Grafik bar chart (Tren Pendapatan, Hunian, Keuangan)
ApexCharts           → Grafik donut/area chart (Dashboard, Laporan)
Select2              → Dropdown searchable untuk form
SweetAlert2          → Alert/confirm dialog yang cantik
Flatpickr            → Date picker untuk filter tanggal
```

### Database — SQLite (Development) / PostgreSQL (Production)

```
SQLite (default Django):
- File: db.sqlite3 di root project
- Tidak perlu install server database
- Cocok untuk development & testing
- TIDAK cocok untuk production (tidak bisa concurrent write)

PostgreSQL (rekomendasi production):
- Database server terpisah
- Support concurrent users
- Full-text search
- Lebih aman dan scalable
```

### Hubungan Setiap Teknologi:

```
┌──────────── BROWSER (User) ────────────┐
│                                         │
│  HTML + CSS (Bootstrap 5 + Materialize)│  ← Tampilan
│  JavaScript (jQuery + Chart.js + dll)  │  ← Interaksi
│  Remix Icon (ri-* class)               │  ← Ikon
│                                         │
└──────────────── HTTP ──────────────────┘
                    │
                    ▼
┌──────────── SERVER (Django) ───────────┐
│                                         │
│  URL Routing → Views → Templates       │  ← Alur utama
│  Models ←→ ORM ←→ Database             │  ← Data
│  Forms → Validasi → Save               │  ← Input
│  Middleware → CSRF, Session, Auth      │  ← Keamanan
│                                         │
└──────────────── ORM ───────────────────┘
                    │
                    ▼
┌──────────── DATABASE (SQLite) ─────────┐
│                                         │
│  Tabel: properti, kamar, penyewa, dll  │
│  Relasi: ForeignKey, ManyToMany        │
│                                         │
└─────────────────────────────────────────┘
```

---

## D. Persiapan & Instalasi dari Awal

### Langkah 1: Install Python

```bash
# Download Python 3.10+ dari https://www.python.org/downloads/
# PENTING: Centang "Add Python to PATH" saat install!

# Verifikasi instalasi:
python --version
# Output yang diharapkan: Python 3.13.1 (atau versi 3.10+)

pip --version
# Output: pip 24.x from ...
```

### Langkah 2: Clone / Download Project

```bash
# Jika dari Git:
git clone <url_repository> SIMKOS-Software
cd SIMKOS-Software

# Jika dari file ZIP:
# Extract ke folder yang diinginkan
# Buka terminal di folder tersebut
```

### Langkah 3: Buat Virtual Environment

```bash
python -m venv env

# Aktifkan venv:
# Windows CMD:
env\Scripts\activate
# Windows PowerShell:
env\Scripts\Activate.ps1
# Linux/Mac:
source env/bin/activate

# Tanda berhasil: ada (env) di awal prompt terminal
# (env) PS D:\SIMKOS-Software>
```

### Langkah 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Langkah 5: Migrasi Database

```bash
python manage.py migrate
```

### Langkah 6: Buat Superuser (Admin Pertama)

```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: admin123
```

### Langkah 7: Jalankan Server

```bash
python manage.py runserver
# Buka browser → http://127.0.0.1:8000/
# → Login → Masuk ke Dashboard SIMKOS
```

---

## E. Cara Menjalankan Project

### Perintah `manage.py` yang PENTING:

```bash
# ═══ MENJALANKAN SERVER ═══
python manage.py runserver

# ═══ DATABASE ═══
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations

# ═══ USER ═══
python manage.py createsuperuser
python manage.py changepassword admin

# ═══ DEBUGGING ═══
python manage.py shell
#   >>> from apps.properti.models import Properti
#   >>> Properti.objects.count()

python manage.py check

# ═══ STATIC FILES (Production) ═══
python manage.py collectstatic
```

---

## F. Arsitektur & Alur Kerja Django

### Alur Request-Response:

```
                                                    ┌────────────────┐
PENGGUNA                                            │  config/       │
types URL ──────► Browser sends ──────────────────► │  urls.py       │
                  HTTP Request                      │  (URL Router)  │
                  GET /properti/list/                └───────┬────────┘
                                                            │
              ┌─────────────────────────────────────────┐   │
              │ LANGKAH 1-3: URL MATCHING               │   │
              │                                         │   │
              │ 1. Django terima request                │   │
              │ 2. Cari match di config/urls.py         │   │
              │    → path("properti/", include(...))    │   │
              │ 3. Lanjut ke apps/properti/urls.py      │   │
              │    → path('list/', PropertiListView)    │   │
              └─────────────────────────────────────────┘   │
                                                            ▼
                                                    ┌────────────────┐
              ┌─────────────────────────────────────│  apps/properti/│
              │ LANGKAH 4-6: PERMISSION + VIEW      │  views.py      │
              │                                     └───────┬────────┘
              │ 4. Mixin cek permission                     │
              │ 5. View get_queryset() → query DB           │
              │ 6. View get_context_data() → siapkan data   │
              └─────────────────────────────────────────────┘
                                                            │
                                                            ▼
                                                     ┌────────────────┐
              ┌──────────────────────────────────────│  templates/    │
              │ LANGKAH 7-8: TEMPLATE RENDERING      │  properti/     │
              │                                      │  *.html        │
              │ 7. Template engine gabungkan          └───────┬────────┘
              │    HTML + data context                        │
              │ 8. Render → Generate HTML lengkap             │
              └───────────────────────────────────────────────┘
```

### Pattern MVT (Model-View-Template):

```
Django menggunakan MVT (Model-View-Template):

┌──────────┐     ┌──────────┐     ┌──────────┐
│  MODEL   │ ←→  │   VIEW   │ ←→  │ TEMPLATE │
│          │     │          │     │          │
│ Data &   │     │ Logika   │     │ Tampilan │
│ Database │     │ Bisnis   │     │ HTML     │
│          │     │ + Routing│     │          │
│ models.py│     │ views.py │     │ *.html   │
└──────────┘     └──────────┘     └──────────┘
```

---

## G. Peta Modul SIMKOS

### Struktur Folder Utama:

```
d:\SIMKOS-Software\                ← ROOT PROJECT
├── config/                        ← Konfigurasi Django
│   ├── settings.py               ← Pengaturan utama
│   ├── urls.py                   ← URL router utama
│   ├── template.py               ← Konfigurasi tema Materialize
│   └── wsgi.py / asgi.py        ← Entry point production
│
├── apps/                          ← 16+ MODUL SIMKOS (yang kita buat)
│   ├── core/                     ← Permission system (mixin, helper)
│   ├── dashboard/                ← Halaman dashboard utama
│   ├── properti/                 ← Properti, Tipe Kamar, Kamar
│   ├── penyewa/                  ← Data penyewa kost
│   ├── sewa/                     ← Kontrak sewa, tagihan, pembayaran
│   ├── biaya/                    ← Biaya operasional kost
│   ├── laporan/                  ← Laporan (hunian, keuangan, dll)
│   ├── hr/                       ← HR / Karyawan KOS
│   ├── ai_assistant/             ← AI Assistant (chat, dashboard, setting)
│   ├── user_management/          ← Kelola user
│   ├── permission_management/    ← Kelola role & permission
│   ├── pengaturan/               ← Pengaturan perusahaan & profil
│   ├── automation/               ← Notifikasi Telegram
│   └── activity_log/             ← Log aktivitas
│
├── auth/                          ← Autentikasi (login, register)
├── web_project/                   ← Template engine (Materialize)
│
├── templates/                     ← 60+ template HTML
│   ├── layout/                   ← Layout system (Materialize bawaan)
│   ├── dashboard/                ← Template dashboard utama
│   ├── properti/                 ← Template modul properti
│   ├── penyewa/                  ← Template modul penyewa
│   ├── sewa/                     ← Template modul sewa
│   ├── laporan/                  ← Template laporan
│   ├── ai_assistant/             ← Template AI assistant
│   └── ...                       ← Template modul lainnya
│
├── static/                        ← Asset statis (CSS, JS, gambar)
├── media/                         ← File upload (foto properti, KTP penyewa)
├── db.sqlite3                     ← Database SQLite
├── manage.py                      ← CLI Django
├── requirements.txt               ← Daftar library Python
└── DOKUMENTASI/                   ← File-file ini!
```

### Hubungan Antar Modul:

```
                    ┌──────────────────┐
                    │    DASHBOARD     │
                    │  Ringkasan kost  │
                    └────────┬─────────┘
                             │ ambil data dari:
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
   ┌──────────┐       ┌──────────┐       ┌──────────┐
   │ PROPERTI │       │  SEWA    │       │  BIAYA   │
   │ + Kamar  │◄──────│ Kontrak  │       │ Operasi- │
   │ + Tipe   │       │ Tagihan  │       │  onal    │
   └────┬─────┘       │ Bayar    │       └──────────┘
        │             └────┬─────┘              │
        │                  │                    │
        ▼                  ▼                    │
   ┌──────────┐       ┌──────────┐             │
   │ PENYEWA  │◄──────│ TAGIHAN  │             │
   │  Data    │       │  SEWA    │             │
   │ penghuni │       │ Bulanan  │             │
   └──────────┘       └──────────┘             │
        │                  │                    │
        └──────────────────┼────────────────────┘
                           ▼
                    ┌──────────────┐
                    │   LAPORAN    │
                    │ Hunian,      │
                    │ Keuangan,    │
                    │ Pemasukan    │
                    └──────────────┘
```

---

**Dokumen Selanjutnya:** Untuk penjelasan detail setiap komponen, baca file dokumentasi berikut secara urut:

1. [01_STRUKTUR_PROJECT.md](01_STRUKTUR_PROJECT.md) — Struktur folder & file
2. [02_KONFIGURASI_DJANGO.md](02_KONFIGURASI_DJANGO.md) — Settings, middleware, URL
3. [03_MODEL_DATABASE.md](03_MODEL_DATABASE.md) — Model, field, relasi, ORM
4. [04_VIEWS_DAN_URL.md](04_VIEWS_DAN_URL.md) — CBV/FBV, mixin, routing
5. [05_TEMPLATE_DAN_LAYOUT.md](05_TEMPLATE_DAN_LAYOUT.md) — Template, layout Materialize
6. [06_FORM_DAN_VALIDASI.md](06_FORM_DAN_VALIDASI.md) — Form, validasi
7. [07_SISTEM_PERMISSION_RBAC.md](07_SISTEM_PERMISSION_RBAC.md) — RBAC, permission, caching
8. [08_FITUR_MODUL_SIMKOS.md](08_FITUR_MODUL_SIMKOS.md) — Detail setiap modul SIMKOS
9. [09_TIPS_DAN_BEST_PRACTICE.md](09_TIPS_DAN_BEST_PRACTICE.md) — Tips & debugging
10. [10_KOMPONEN_UI_SNEAT.md](10_KOMPONEN_UI_SNEAT.md) — Komponen UI lengkap
11. [11_PANDUAN_MEMBUAT_MODUL_BARU.md](11_PANDUAN_MEMBUAT_MODUL_BARU.md) — Tutorial step-by-step
12. [12_MIXIN_DAN_CBV_LANJUTAN.md](12_MIXIN_DAN_CBV_LANJUTAN.md) — Mixin & CBV lanjutan
13. [13_API_DAN_AJAX.md](13_API_DAN_AJAX.md) — REST API & AJAX
14. [14_TEMPLATE_TAGS_DAN_FILTERS.md](14_TEMPLATE_TAGS_DAN_FILTERS.md) — Template tags & filters
15. [15_CHARTS_DAN_DASHBOARD.md](15_CHARTS_DAN_DASHBOARD.md) — Charts & dashboard
16. [16_PERBAIKAN_DAN_PENINGKATAN.md](16_PERBAIKAN_DAN_PENINGKATAN.md) — Perbaikan UI/UX
17. [17_KEAMANAN_DAN_DEPLOYMENT.md](17_KEAMANAN_DAN_DEPLOYMENT.md) — Keamanan & deployment
