# 🗄️ 03 — Model & Database — Penjelasan Sangat Detail

## A. Apa itu Model Django? Kenapa Pakai Model?

### Masalah Tanpa Model (SQL mentah):
```python
# TANPA MODEL — harus tulis SQL mentah (rawan error, tidak portable)
import sqlite3
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE properti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama VARCHAR(200) NOT NULL,
        alamat TEXT NOT NULL,
        tipe VARCHAR(20) DEFAULT 'kost'
    )
""")
# Problem:
# 1. SQL berbeda untuk setiap database (SQLite vs PostgreSQL vs MySQL)
# 2. Tidak ada validasi otomatis
# 3. Tidak ada relasi yang jelas
# 4. Rawan SQL injection jika tidak hati-hati
```

### Solusi Django Model (ORM):
```python
# DENGAN MODEL — tulis Python, Django generate SQL otomatis
class Properti(models.Model):
    nama = models.CharField(max_length=200)
    alamat = models.TextField()
    tipe = models.CharField(max_length=20, default='kost')
```

**ORM (Object-Relational Mapping)** = teknik mengubah class Python menjadi tabel database. Django ORM otomatis:
- Generate SQL yang tepat untuk database yang digunakan
- Menyediakan validasi tipe data
- Mencegah SQL injection
- Mendukung relasi antar tabel

---

## B. Anatomi Model — Baris per Baris

### Model Properti (Contoh Utama SIMKOS):

```python
# File: apps/properti/models.py

from django.db import models
# ↑ Import modul 'models' dari package 'django.db'
# 'django.db' = Django Database module
# 'models' berisi semua class untuk definisi model:
#   - models.Model (class dasar semua model)
#   - models.CharField, models.IntegerField, dll (tipe field)
#   - models.ForeignKey (relasi antar tabel)
# Dari mana? Otomatis terinstall saat install Django

from django.contrib.auth.models import User
# ↑ Import model User BAWAAN Django
# User sudah punya: id, username, email, password, first_name, last_name,
#                   is_active, is_staff, is_superuser, date_joined
# Kita TIDAK perlu membuat model User sendiri — Django sudah sediakan
# Dari mana? Package django.contrib.auth (sudah di INSTALLED_APPS)


class Properti(models.Model):
    """Model untuk data PROPERTI (kost atau kontrakan)."""
    # ↑ class Properti = nama model (akan menjadi nama tabel: properti_properti)
    # (models.Model) = Properti mewarisi (inherit) dari class Model
    #   → Artinya Properti otomatis punya id, save(), delete(), objects, dll
    #   → Ini konsep OOP: Inheritance (pewarisan)
    
    TIPE_CHOICES = [
        ('kost', 'Kost'),
        ('kontrakan', 'Kontrakan'),
        ('apartemen', 'Apartemen'),
        ('rumah', 'Rumah Sewa'),
    ]
    # ↑ Choices = daftar pilihan yang valid untuk field tipe
    #   Format: [(value_db, label_tampilan), ...]
    #   Di form: ditampilkan sebagai dropdown/select
    
    nama = models.CharField(max_length=200, verbose_name="Nama Properti")
    # ↑ Field 'nama' bertipe CharField
    #   CharField = karakter/teks pendek → menjadi kolom VARCHAR di database
    #   max_length=200 → maksimal 200 karakter (WAJIB untuk CharField)
    #   verbose_name="Nama Properti" → label yang ditampilkan di form/admin
    #
    # Di database menjadi: nama VARCHAR(200) NOT NULL
    # Contoh data: "Kost Melati Indah", "Kontrakan Mawar"
    
    tipe = models.CharField(max_length=20, choices=TIPE_CHOICES, default='kost',
                            verbose_name="Tipe Properti")
    # ↑ choices=TIPE_CHOICES → validasi: hanya value dari TIPE_CHOICES yang diterima
    #   default='kost' → jika tidak diisi, otomatis 'kost'
    
    alamat = models.TextField(verbose_name="Alamat Lengkap")
    # ↑ TextField = teks panjang tanpa batas → menjadi kolom TEXT di database
    #   Tanpa blank=True → field ini WAJIB diisi
    
    kota = models.CharField(max_length=100, blank=True, null=True,
                            verbose_name="Kota/Kabupaten")
    # ↑ blank=True → boleh KOSONG di FORM (user tidak wajib mengisi)
    #   null=True → boleh NULL di DATABASE (kolom bisa berisi NULL)
    #
    # PENTING: blank vs null
    #   blank=True → validasi form: "field ini opsional, boleh kosong"
    #   null=True → database: "kolom ini boleh berisi NULL"
    #   Biasanya keduanya diset bersamaan untuk field opsional
    
    foto = models.ImageField(upload_to='properti/', blank=True, null=True,
                             verbose_name="Foto Properti")
    # ↑ ImageField = upload gambar
    #   upload_to='properti/' → disimpan di folder media/properti/
    #   Contoh path: media/properti/kost_melati.jpg
    #   Membutuhkan library Pillow (pip install Pillow)
    #   Di template: <img src="{{ properti.foto.url }}">
    
    aktif = models.BooleanField(default=True, verbose_name="Aktif")
    # ↑ BooleanField = True / False
    #   default=True → properti baru otomatis aktif
    
    dibuat_oleh = models.ForeignKey(
        User,                                # → Relasi ke tabel auth_user
        on_delete=models.SET_NULL,           # → Jika user dihapus: set NULL
        null=True,                           # → Boleh NULL
        related_name='properti_dibuat'       # → Akses balik: user.properti_dibuat.all()
    )
    # ↑ ForeignKey = relasi Many-to-One
    #   "Banyak properti bisa dibuat oleh satu user"
    #   Di database: kolom dibuat_oleh_id INTEGER REFERENCES auth_user(id)
    #
    #   on_delete = apa yang terjadi jika User (parent) DIHAPUS?
    #     CASCADE   → ikut terhapus (kontrak dihapus → tagihan terhapus)
    #     SET_NULL  → diset NULL (user dihapus → properti tetap ada)
    #     PROTECT   → TIDAK BISA hapus (tipe kamar tidak bisa dihapus jika masih dipakai kamar)
    #     SET_DEFAULT → diset ke nilai default
    #
    #   related_name = nama untuk akses BALIK dari User ke Properti
    #     user.properti_dibuat.all()  → semua properti yang dibuat user ini
    #     Tanpa related_name: user.properti_set.all() (nama default)
    
    dibuat_pada = models.DateTimeField(auto_now_add=True)
    # ↑ DateTimeField = tanggal + waktu → kolom DATETIME di database
    #   auto_now_add=True → otomatis diisi SAAT PERTAMA KALI objek dibuat
    #   Setelah itu TIDAK berubah — jadi ini menandakan "tanggal pembuatan"
    #
    # Contoh output: 2026-02-21 10:30:45.123456
    
    diupdate_pada = models.DateTimeField(auto_now=True)
    # ↑ auto_now=True → otomatis diisi SETIAP KALI objek disimpan (save())
    #   Ini menandakan "terakhir diupdate"
    #   Berbeda dengan auto_now_add yang hanya sekali saat create
    
    class Meta:
        """Konfigurasi metadata model untuk Django."""
        verbose_name = "Properti"          # Nama tampilan singular
        verbose_name_plural = "Properti"   # Nama tampilan plural (di admin)
        ordering = ['nama']                # Urutan default: A-Z berdasarkan nama
        # ordering berlaku otomatis saat Properti.objects.all()
        # ['nama'] = ascending (A-Z)
        # ['-nama'] = descending (Z-A)
        # ['-dibuat_pada', 'nama'] = terbaru dulu, lalu A-Z
    
    def __str__(self):
        """
        Representasi string — dipanggil saat print(properti) atau di dropdown.
        Contoh output: "Kost Melati Indah (Kost)"
        """
        return f"{self.nama} ({self.get_tipe_display()})"
    
    @property
    def total_kamar(self):
        return self.kamar_set.count()
    
    @property
    def kamar_tersedia(self):
        return self.kamar_set.filter(status='tersedia').count()
    
    @property
    def kamar_terisi(self):
        return self.kamar_set.filter(status='terisi').count()
```

**Tabel database yang dihasilkan:**
```sql
-- Django otomatis membuat SQL ini saat migrate:
CREATE TABLE "properti_properti" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "nama" varchar(200) NOT NULL,
    "tipe" varchar(20) NOT NULL,
    "alamat" text NOT NULL,
    "kota" varchar(100) NULL,
    "foto" varchar(100) NULL,
    "aktif" bool NOT NULL DEFAULT 1,
    "dibuat_pada" datetime NOT NULL,
    "diupdate_pada" datetime NOT NULL,
    "dibuat_oleh_id" integer NULL REFERENCES "auth_user" ("id")
);
```

**Contoh data di database:**
```
┌────┬─────────────────────┬───────────┬──────────────────────────┬─────────────┐
│ id │ nama                │ tipe      │ alamat                   │ aktif       │
├────┼─────────────────────┼───────────┼──────────────────────────┼─────────────┤
│ 1  │ Kost Melati Indah   │ kost      │ Jl. Merpati No. 15      │ True        │
│ 2  │ Kontrakan Mawar     │ kontrakan │ Jl. Mawar No. 10        │ True        │
│ 3  │ Apartemen Cempaka   │ apartemen │ Jl. Cempaka Blok A      │ True        │
└────┴─────────────────────┴───────────┴──────────────────────────┴─────────────┘
```

---

## C. Semua Jenis Field — dengan Contoh Nyata

### Field Teks

```python
# CharField — Teks pendek (WAJIB ada max_length)
nama = models.CharField(max_length=200)
# Database: VARCHAR(200) NOT NULL
# Kapan pakai: Nama properti, nama penyewa, nomor kamar
# Contoh data: "Kost Melati Indah", "Kamar 101A"

# TextField — Teks panjang (TANPA max_length)
alamat = models.TextField(verbose_name="Alamat Lengkap")
# Database: TEXT NOT NULL
# Kapan pakai: Alamat, keterangan, catatan panjang
# Contoh data: "Jl. Merpati No. 15, Kel. Dago, Kec. Coblong, Bandung 40135"

# EmailField — Email (CharField + validasi format email)
email = models.EmailField(max_length=100, blank=True, null=True)
# Database: VARCHAR(100) NULL
# Validasi otomatis: harus format xxx@yyy.zzz
# Contoh data: "budi@gmail.com"
```

### Field Angka

```python
# DecimalField — Angka desimal PRESISI (untuk uang!)
harga_bulanan = models.DecimalField(max_digits=12, decimal_places=0, default=0)
# Database: DECIMAL(12,0)
# max_digits=12 → total digit maksimal
# decimal_places=0 → tanpa desimal (Rupiah bulat)
# Range: 0 sampai 999,999,999,999
# Contoh data: 1500000, 2000000
# KENAPA DecimalField bukan FloatField untuk harga?
#   FloatField menggunakan floating-point (binary) → 0.1 + 0.2 = 0.30000000000000004
#   DecimalField menggunakan fixed-point → 0.1 + 0.2 = 0.3 (PRESISI)
#   Untuk uang, SELALU gunakan DecimalField!

# IntegerField — Bilangan bulat
lantai = models.PositiveIntegerField(default=1)
# Database: INTEGER UNSIGNED
# Contoh data: 1, 2, 3
```

### Field Tanggal & Waktu

```python
# DateTimeField — Tanggal + waktu
dibuat_pada = models.DateTimeField(auto_now_add=True)
# auto_now_add=True → otomatis saat CREATE (hanya sekali)
# Contoh output: 2026-02-21 17:30:45.123456

diupdate_pada = models.DateTimeField(auto_now=True)
# auto_now=True → otomatis setiap kali SAVE (update terakhir)

tanggal_mulai = models.DateField(verbose_name="Tanggal Mulai Sewa")
# DateField — hanya tanggal (tanpa waktu)
# Contoh output: 2026-01-15
```

### Field Boolean & File

```python
# BooleanField — True / False
aktif = models.BooleanField(default=True)
# Database: BOOLEAN (0 atau 1)
# default=True → jika tidak diisi, otomatis True
# Di form: checkbox ☑

# ImageField — Upload gambar
foto = models.ImageField(upload_to='properti/', blank=True, null=True)
# upload_to='properti/' → disimpan di folder media/properti/
# Contoh path: media/properti/kost_melati.jpg
# Membutuhkan library Pillow (pip install Pillow)
# Di template: <img src="{{ properti.foto.url }}">
```

---

## D. Relasi Antar Model — Penjelasan Sangat Detail

### 1. ForeignKey (Many-to-One) — Relasi Paling Umum

**Konsep:** Banyak kamar bisa berada di SATU properti yang sama.

```python
class Kamar(models.Model):
    properti = models.ForeignKey(
        Properti,                    # → Tabel yang direferensikan
        on_delete=models.CASCADE,    # → Jika Properti dihapus, kamar ikut terhapus
        verbose_name="Properti"      # → Label di form
    )
    tipe_kamar = models.ForeignKey(
        TipeKamar,                   # → Tabel tipe kamar
        on_delete=models.SET_NULL,   # → Jika tipe dihapus, kamar tetap ada
        null=True,                   # → Boleh tanpa tipe
        verbose_name="Tipe Kamar"
    )
```

**Di database:**
```
Tabel: properti_kamar
┌────┬──────────────┬───────────────┬─────────────┐
│ id │ nomor_kamar  │ properti_id   │ tipe_kamar_id│
├────┼──────────────┼───────────────┼─────────────┤
│ 1  │ 101          │ 1             │ 1           │  ← Kamar 101 di properti id=1
│ 2  │ 102          │ 1             │ 1           │  ← Kamar 102 di properti id=1
│ 3  │ 201          │ 1             │ 2           │  ← Kamar 201 di properti id=1
│ 4  │ A1           │ 2             │ 3           │  ← Kamar A1 di properti id=2
└────┴──────────────┴───────────────┴─────────────┘
```

**Cara akses di Python:**
```python
# Dari Kamar → Properti (MAJU / forward)
kamar = Kamar.objects.get(pk=1)
print(kamar.properti)             # Output: Kost Melati Indah (Kost)
print(kamar.properti.nama)        # Output: Kost Melati Indah
print(kamar.properti.alamat)      # Output: Jl. Merpati No. 15

# Dari Properti → Kamar (BALIK / reverse) menggunakan default related_name
properti = Properti.objects.get(pk=1)
print(properti.kamar_set.all())   # Output: <QuerySet [Kamar 101, Kamar 102, Kamar 201]>
print(properti.kamar_set.count()) # Output: 3
# ↑ 'kamar_set' = nama default reverse relation (model_set)
```

### 2. OneToOneField — Satu ke Satu

```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
```

**Konsep:** Setiap User punya TEPAT 1 Profile, dan sebaliknya.

**Cara akses:**
```python
user = User.objects.get(username='admin')
print(user.profile)        # Output: admin (Profile object)
print(user.profile.role)   # Output: SUPERUSER
print(user.profile.phone)  # Output: 081234567890
```

---

## E. Property dan Method Spesial

### Property `total_kamar` — Hitung Total Kamar di Properti

```python
@property
def total_kamar(self):
    return self.kamar_set.count()
```

**Penjelasan setiap bagian:**
- `@property` → Decorator Python yang membuat method bisa diakses seperti attribute
  - Tanpa `@property`: `properti.total_kamar()` → pakai tanda kurung
  - Dengan `@property`: `properti.total_kamar` → tanpa tanda kurung (lebih natural)
- `self.kamar_set` → Semua record Kamar yang terkait properti ini (reverse relation)
- `.count()` → SQL: `SELECT COUNT(*) FROM properti_kamar WHERE properti_id=self.id`

**Contoh:**
```python
properti = Properti.objects.get(nama="Kost Melati Indah")
# Kamar di database:
# Kamar 101 (Tersedia)
# Kamar 102 (Terisi)
# Kamar 201 (Terisi)
# Kamar 202 (Perbaikan)

print(properti.total_kamar)     # Output: 4
print(properti.kamar_tersedia)  # Output: 1
print(properti.kamar_terisi)    # Output: 2
```

### Method `generate_nomor()` — Auto-Generate Nomor Kontrak

```python
def generate_nomor(self):
    """Generate nomor kontrak: KTR/2026/02/0001"""
    from datetime import datetime
    now = datetime.now()
    prefix = f"KTR/{now.year}/{now.month:02d}"
    
    last = KontrakSewa.objects.filter(
        nomor_kontrak__startswith=prefix
    ).order_by('-nomor_kontrak').first()
    
    if last:
        last_number = int(last.nomor_kontrak.split('/')[-1])
        new_number = last_number + 1
    else:
        new_number = 1
    
    return f"{prefix}/{new_number:04d}"
```

**Langkah demi langkah:**
```
Bulan = Februari 2026
1. prefix = "KTR/2026/02"
2. Query: KontrakSewa WHERE nomor_kontrak LIKE 'KTR/2026/02%' ORDER BY DESC LIMIT 1
3. Hasil: last.nomor_kontrak = "KTR/2026/02/0005"
4. split('/') = ["KTR", "2026", "02", "0005"] → [-1] = "0005" → int = 5
5. new_number = 5 + 1 = 6
6. f"KTR/2026/02/{6:04d}" = "KTR/2026/02/0006"
```

---

## F. Operasi Database (ORM) — Contoh Lengkap dengan Output

### CREATE — Membuat Data Baru
```python
# Cara 1: create() — langsung simpan ke database
properti = Properti.objects.create(
    nama="Kost Melati Indah",
    tipe="kost",
    alamat="Jl. Merpati No. 15, Bandung"
)
print(properti)     # Output: Kost Melati Indah (Kost)
print(properti.id)  # Output: 1 (auto-generated)
print(properti.dibuat_pada)  # Output: 2026-02-21 17:30:00

# Cara 2: instantiate lalu save()
kamar = Kamar(properti=properti, nomor_kamar="101", lantai=1)
kamar.save()  # Baru disimpan ke database saat save() dipanggil
```

### READ — Membaca Data
```python
# Semua data
semua = Properti.objects.all()
# Output: <QuerySet [<Properti: Kost Melati Indah>, <Properti: Kontrakan Mawar>]>

# Filter
kost_saja = Properti.objects.filter(tipe='kost')
# Output: <QuerySet [<Properti: Kost Melati Indah>]>

# Filter via relasi (double underscore)
kamar_lantai_1 = Kamar.objects.filter(properti__nama="Kost Melati Indah", lantai=1)
# ↑ properti__nama → "ikuti relasi FK ke Properti, lalu filter field nama"
#   Double underscore (__) = "traverse relation"

# Satu data spesifik
properti = Properti.objects.get(pk=1)  # pk = primary key
# Output: <Properti: Kost Melati Indah>
# ⚠ get() akan ERROR jika data tidak ditemukan (DoesNotExist) atau lebih dari 1

# Filter lanjutan
mahal = Kamar.objects.filter(tipe_kamar__harga_bulanan__gte=2000000)  # gte = ≥
murah = Kamar.objects.filter(tipe_kamar__harga_bulanan__lt=1000000)   # lt = <
cari = Penyewa.objects.filter(nama__icontains="budi")  # icontains = case-insensitive LIKE
```

### UPDATE — Mengubah Data
```python
properti = Properti.objects.get(pk=1)
properti.nama = "Kost Melati Indah Baru"
properti.save()
# SQL: UPDATE properti_properti SET nama='Kost Melati Indah Baru' WHERE id=1

# Bulk update (tanpa load object — lebih cepat)
Kamar.objects.filter(properti__id=1).update(status='maintenance')
# SQL: UPDATE properti_kamar SET status='maintenance' WHERE properti_id=1
```

### DELETE — Menghapus Data
```python
kamar = Kamar.objects.get(pk=1)
kamar.delete()
# SQL: DELETE FROM properti_kamar WHERE id=1
# Output: (1, {'properti.Kamar': 1})
# ↑ Artinya: 1 objek dihapus, yaitu 1 Kamar
```

---

## G. Diagram Relasi Lengkap — SIMKOS

```
────────────────────── MODUL PROPERTI ──────────────────────
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  TipeKamar   │◄─FK─│    Kamar     │─FK─►│  Properti    │
│              │     │              │     │              │
│ id           │     │ id           │     │ id           │
│ nama         │     │ nomor_kamar  │     │ nama         │
│ harga_bulanan│     │ lantai       │     │ tipe         │
│ fasilitas    │     │ status       │     │ alamat       │
└──────────────┘     │ pos_x, pos_y │     │ aktif        │
                     │ width, height│     └──────────────┘
                     └──────┬───────┘
                            │ kamar disewakan via:
                            ▼
────────────────── MODUL SEWA / KONTRAK ──────────────────
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Penyewa    │◄─FK─│ KontrakSewa  │─FK─►│    Kamar     │
│              │     │              │     │              │
│ id           │     │ id           │     │ (lihat atas) │
│ nama         │     │ nomor_kontrak│     └──────────────┘
│ nik          │     │ tanggal_mulai│
│ telepon      │     │ tanggal_akhir│
│ foto_ktp     │     │ harga_sewa   │
│ status       │     │ deposit      │
└──────────────┘     │ status       │
                     └──────┬───────┘
                            │ kontrak menghasilkan:
                            ▼
                     ┌──────────────┐
                     │ TagihanSewa  │
                     │              │
                     │ id           │
                     │ nomor_tagihan│
                     │ periode_bulan│
                     │ periode_tahun│
                     │ jumlah       │
                     │ jatuh_tempo  │
                     │ status       │
                     └──────┬───────┘
                            │ tagihan dibayar via:
                            ▼
                     ┌──────────────────┐
                     │ PembayaranSewa   │
                     │                  │
                     │ id               │
                     │ nomor_pembayaran │
                     │ jumlah_bayar     │
                     │ tanggal_bayar    │
                     │ metode_bayar     │
                     │ bukti            │
                     └──────────────────┘

────────────────────── MODUL BIAYA ──────────────────────
┌────────────────┐       ┌──────────────────────┐
│ KategoriBiaya  │◄──FK──│   TransaksiBiaya     │
│                │       │                      │
│ id             │       │ id                   │
│ nama           │       │ nomor_transaksi      │
│ deskripsi      │       │ tanggal              │
└────────────────┘       │ kategori_id (FK)     │
                         │ jumlah               │ ← nominal biaya
                         │ keterangan           │
                         │ bukti (ImageField)   │ ← foto kuitansi
                         │ dibuat_oleh (FK)     │
                         └──────────────────────┘
                         Contoh: Bayar listrik Rp 2.500.000
```

---

## H. ERD (Entity Relationship Diagram) Lengkap — Seluruh Model SIMKOS

### Kenapa ERD Penting?

**ERD (Entity Relationship Diagram)** = peta visual yang menunjukkan SEMUA tabel database dan bagaimana mereka saling terhubung.

### Daftar Lengkap Model (Dikelompokkan per Domain):

```
╔══════════════════════════════════════════════════════════════════════╗
║                    SELURUH MODEL SISTEM SIMKOS                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  🔐 AUTH & USER (3 model)                                           ║
║  ├── User (bawaan Django)  ← auth_user                              ║
║  ├── Profile               ← auth_profile (OneToOne → User)        ║
║  └── RolePermission        ← core_rolepermission                    ║
║                                                                      ║
║  🏠 PROPERTI (3 model)                                              ║
║  ├── Properti              ← properti_properti                      ║
║  ├── TipeKamar             ← properti_tipekamar                     ║
║  └── Kamar                 ← properti_kamar                         ║
║                                                                      ║
║  👤 PENYEWA (1 model)                                               ║
║  └── Penyewa               ← penyewa_penyewa                       ║
║                                                                      ║
║  📋 SEWA / KONTRAK (3 model)                                       ║
║  ├── KontrakSewa           ← sewa_kontraksewa                      ║
║  ├── TagihanSewa           ← sewa_tagihansewa                      ║
║  └── PembayaranSewa        ← sewa_pembayaransewa                   ║
║                                                                      ║
║  💸 BIAYA (2 model)                                                 ║
║  ├── KategoriBiaya         ← biaya_kategoribiaya                    ║
║  └── TransaksiBiaya        ← biaya_transaksibiaya                   ║
║                                                                      ║
║  👥 HR / KARYAWAN KOS (6 model)                                     ║
║  ├── Departemen            ← hr_departemen                          ║
║  ├── Jabatan               ← hr_jabatan                             ║
║  ├── Karyawan              ← hr_karyawan                            ║
║  ├── FotoWajah             ← hr_fotowajah                           ║
║  ├── Absensi               ← hr_absensi                             ║
║  └── Penggajian            ← hr_penggajian                          ║
║                                                                      ║
║  🤖 AI ASSISTANT (2 model)                                          ║
║  ├── AISettings            ← ai_assistant_aisettings                ║
║  └── ChatHistory           ← ai_assistant_chathistory               ║
║                                                                      ║
║  ⚙️ SISTEM & AUTOMATION (5 model)                                   ║
║  ├── PengaturanPerusahaan  ← pengaturan_pengaturanperusahaan        ║
║  ├── TemplateCetak         ← pengaturan_templatecetak               ║
║  ├── PengaturanTelegram    ← automation_pengaturantelegram          ║
║  ├── TemplatePesan         ← automation_templatepesan               ║
║  └── LogNotifikasi         ← automation_lognotifikasi               ║
║                                                                      ║
║  📊 AUDIT (1 model)                                                 ║
║  └── UserActivity          ← activity_log_useractivity              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

### ERD Visual — Relasi Antar Semua Model:

```
═══════════════════════════════════════════════════════════════════════
                         AUTH & USER DOMAIN
═══════════════════════════════════════════════════════════════════════

┌─────────────────┐   OneToOne   ┌─────────────────────┐
│   User          │◄════════════►│  Profile             │
│   (Django)      │              │                     │
│   ─────────     │              │  ─────────          │
│   id            │              │  id                 │
│   username      │              │  user_id (FK→User)  │
│   email         │              │  role (VARCHAR)     │
│   password (hash)│             │  phone              │
│   first_name    │              │  avatar             │
│   last_name     │              └─────────────────────┘
│   is_active     │
│   is_staff      │              ┌─────────────────────────┐
│   date_joined   │              │  RolePermission          │
└────────┬────────┘              │  ─────────               │
         │  role dipakai sbg key │  role (VARCHAR)          │
         └──────────────────────►│  module (VARCHAR)         │
                                 │  sub_module (VARCHAR)     │
                                 │  can_view (BOOLEAN)       │
                                 │  can_create (BOOLEAN)     │
                                 │  can_edit (BOOLEAN)       │
                                 │  can_delete (BOOLEAN)     │
                                 └───────────────────────────┘


═══════════════════════════════════════════════════════════════════════
                       PROPERTI DOMAIN
═══════════════════════════════════════════════════════════════════════

┌──────────────┐       ┌──────────────────┐       ┌──────────────┐
│  TipeKamar   │◄──FK──│      Kamar       │──FK──►│   Properti   │
│              │       │                  │       │              │
│ id           │       │ id               │       │ id           │
│ nama         │       │ nomor_kamar      │       │ nama         │
│ harga_bulanan│       │ lantai           │       │ tipe         │
│ fasilitas    │       │ status           │       │ alamat       │
│ deskripsi    │       │ pos_x, pos_y     │       │ kota         │
│ aktif        │       │ width, height    │       │ foto         │
└──────────────┘       │ properti_id (FK) │       │ pemilik      │
                       │ tipe_kamar_id(FK)│       │ aktif        │
                       └────────┬─────────┘       └──────────────┘
                                │
                                │  Kamar disewakan via KontrakSewa
                                ▼

═══════════════════════════════════════════════════════════════════════
                         SEWA DOMAIN
═══════════════════════════════════════════════════════════════════════

┌──────────────┐       ┌──────────────────┐       ┌──────────────┐
│   Penyewa    │◄──FK──│  KontrakSewa     │──FK──►│    Kamar     │
│              │       │                  │       │              │
│ id           │       │ id               │       │ (lihat atas) │
│ nama         │       │ nomor_kontrak    │       └──────────────┘
│ nik          │       │ penyewa_id (FK)  │
│ jenis_kelamin│       │ kamar_id (FK)    │
│ telepon      │       │ tanggal_mulai    │
│ email        │       │ tanggal_selesai  │
│ alamat_asal  │       │ harga_sewa       │
│ pekerjaan    │       │ deposit          │
│ foto_ktp     │       │ status           │
│ kontak_darurat│      │ catatan          │
│ status       │       │ dibuat_oleh(FK)  │
└──────────────┘       └──────┬───────────┘
                              │
                              │  Kontrak menghasilkan tagihan bulanan:
                              ▼
                       ┌──────────────────┐
                       │  TagihanSewa     │
                       │                  │
                       │ id               │
                       │ nomor_tagihan    │ ← TGH/2026/02/0001
                       │ kontrak_id (FK)  │
                       │ periode_bulan    │
                       │ periode_tahun    │
                       │ jumlah           │
                       │ jatuh_tempo      │
                       │ status           │ ← belum_bayar/lunas/sebagian/terlambat
                       │ catatan          │
                       └──────┬───────────┘
                              │
                              │  Penyewa membayar tagihan:
                              ▼
                       ┌──────────────────┐
                       │ PembayaranSewa   │
                       │                  │
                       │ id               │
                       │ nomor_pembayaran │ ← BYR/2026/02/0001
                       │ tagihan_id (FK)  │
                       │ jumlah_bayar     │
                       │ tanggal_bayar    │
                       │ metode_bayar     │ ← tunai/transfer/ewallet/qris
                       │ bukti            │ ← ImageField (foto bukti)
                       │ catatan          │
                       │ dibuat_oleh (FK) │
                       └──────────────────┘

        Status Flow Tagihan:
        Belum Bayar → (bayar sebagian) → Bayar Sebagian → (bayar sisa) → Lunas
        Belum Bayar → (lewat jatuh tempo) → Terlambat → (bayar) → Lunas


═══════════════════════════════════════════════════════════════════════
                      BIAYA DOMAIN (CRUD)
═══════════════════════════════════════════════════════════════════════

┌────────────────┐       ┌──────────────────────┐
│ KategoriBiaya  │◄──FK──│   TransaksiBiaya     │
│                │       │                      │
│ id             │       │ id                   │
│ nama           │       │ nomor_transaksi      │ ← EXP/2026/02/0001
│ deskripsi      │       │ tanggal              │
│ aktif          │       │ kategori_id (FK)     │
└────────────────┘       │ jumlah               │ ← nominal biaya
                         │ keterangan           │
                         │ bukti (ImageField)   │ ← foto kuitansi
                         │ properti_id (FK)     │ ← properti mana
                         │ dibuat_oleh (FK)     │
                         └──────────────────────┘

Contoh Transaksi Biaya:
EXP/2026/02/0001 — Listrik — Rp 2.500.000 — Kost Melati Indah
EXP/2026/02/0002 — Perbaikan — Rp 350.000 — Pipa bocor kamar 103


═══════════════════════════════════════════════════════════════════════
                     HR / KARYAWAN KOS DOMAIN
═══════════════════════════════════════════════════════════════════════

┌──────────────┐      ┌──────────────┐      ┌──────────────────┐
│  Departemen  │◄─FK──│   Jabatan    │◄─FK──│    Karyawan      │
│              │      │              │      │                  │
│ id           │      │ id           │      │ id               │
│ nama         │      │ nama         │      │ user_id (FK)     │
│ deskripsi    │      │ departemen_id│      │ nip              │
└──────────────┘      │ gaji_pokok   │      │ nama_lengkap     │
                      └──────────────┘      │ jabatan_id (FK)  │
                                            │ foto             │
                           ┌────────────────┤ status           │
                           │                └──────────────────┘
                           ▼
                    ┌──────────────┐            ┌──────────────┐
                    │   Absensi    │            │  Penggajian  │
                    │              │            │              │
                    │ karyawan(FK) │            │ karyawan(FK) │
                    │ tanggal      │            │ periode      │
                    │ jam_masuk    │            │ gaji_pokok   │
                    │ jam_keluar   │            │ tunjangan    │
                    │ status       │            │ potongan     │
                    └──────────────┘            │ total_gaji   │
                                               └──────────────┘
```

---

## I. Alur Data Keuangan — Bagaimana Uang Mengalir di SIMKOS

```
╔═══════════════════════════════════════════════════════════════════╗
║                    ALUR KEUANGAN SIMKOS                          ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  PEMASUKAN (Uang Masuk):                                         ║
║  ──────────────────────                                          ║
║  Penyewa bayar tagihan sewa → PembayaranSewa                    ║
║  Rp 1.500.000 (transfer BCA) → masuk pemasukan                  ║
║                                                                   ║
║  PENGELUARAN (Uang Keluar):                                      ║
║  ──────────────────────────                                      ║
║  Bayar listrik → TransaksiBiaya → Rp 2.500.000                  ║
║  Bayar air    → TransaksiBiaya → Rp 800.000                     ║
║  Gaji karyawan → TransaksiBiaya → Rp 2.000.000                  ║
║  Perbaikan    → TransaksiBiaya → Rp 350.000                     ║
║                                                                   ║
║  LABA BERSIH:                                                     ║
║  ───────────                                                     ║
║  Total Pemasukan - Total Pengeluaran = Laba Bersih               ║
║  Margin (%) = (Laba / Pemasukan) × 100                           ║
║                                                                   ║
║  LAPORAN:                                                         ║
║  ───────                                                         ║
║  Dashboard    → query PembayaranSewa + TransaksiBiaya            ║
║  Lap. Hunian  → query Properti + Kamar (terisi vs tersedia)      ║
║  Lap. Keuangan → query semua (pemasukan - pengeluaran)           ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## J. Query ORM Lanjutan — Contoh dari SIMKOS

### Aggregate — Menghitung Total
```python
from django.db.models import Sum, Count, Q

# Total pemasukan bulan ini
from apps.sewa.models import PembayaranSewa
total = PembayaranSewa.objects.filter(
    tanggal_bayar__month=2,
    tanggal_bayar__year=2026
).aggregate(total=Sum('jumlah_bayar'))['total'] or 0
# Output: Decimal('15000000')

# Total kamar per status
from apps.properti.models import Kamar
stats = Kamar.objects.values('status').annotate(jumlah=Count('id'))
# Output: [{'status': 'tersedia', 'jumlah': 5}, {'status': 'terisi', 'jumlah': 12}, ...]
```

### Select Related — Optimasi Query
```python
# TANPA select_related (N+1 masalah!):
tagihan_list = TagihanSewa.objects.all()
for t in tagihan_list:
    print(t.kontrak.penyewa.nama)  # Setiap loop = 2 query tambahan!
# Total: 1 + (N × 2) query → LAMBAT jika banyak data!

# DENGAN select_related (1 query saja!):
tagihan_list = TagihanSewa.objects.select_related(
    'kontrak__penyewa', 'kontrak__kamar__properti'
).all()
for t in tagihan_list:
    print(t.kontrak.penyewa.nama)  # Sudah di-cache, tanpa query tambahan
# Total: 1 query (JOIN) → JAUH lebih cepat!
```

### Q Objects — Conditional Filter
```python
from django.db.models import Q

# Cari penyewa yang nama ATAU telepon mengandung keyword
keyword = "budi"
penyewa = Penyewa.objects.filter(
    Q(nama__icontains=keyword) | Q(telepon__icontains=keyword)
)
# SQL: WHERE (nama LIKE '%budi%' OR telepon LIKE '%budi%')
```

---

*Lanjut ke [04_VIEWS_DAN_URL.md](04_VIEWS_DAN_URL.md) →*
