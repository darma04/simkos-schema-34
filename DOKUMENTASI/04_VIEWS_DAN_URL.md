# 🔀 04 — Views & URL Routing — Penjelasan SANGAT Detail & Lengkap

## DAFTAR ISI
- [A. Apa itu View?](#a-apa-itu-view)
- [B. FBV vs CBV — Perbandingan Lengkap](#b-fbv-vs-cbv)
- [C. Semua Jenis CBV Bawaan Django](#c-semua-jenis-cbv-bawaan-django)
- [D. Struktur Internal CBV — Method Lifecycle](#d-struktur-internal-cbv)
- [E. Mixin — Menambah Fitur ke View](#e-mixin)
- [F. URL Routing — Detail Lengkap](#f-url-routing)
- [F2. path() vs re_path() — Deep Dive](#f2-path-vs-re_path--deep-dive)
- [F3. Namespacing & Reverse URL — Deep Dive](#f3-namespacing--reverse-url--deep-dive)
- [F4. Error Handlers (404, 403, 500)](#f4-error-handlers-404-403-500)
- [F5. Peta URL Lengkap Semua 14 Modul](#f5-peta-url-lengkap-semua-14-modul)
- [G. TemplateLayout — Custom Layout System](#g-templatelayout)
- [H. Contoh Nyata dari Project](#h-contoh-nyata)
- [I2. apps.py — AppConfig](#i2-appspy--appconfig)
- [I3. context_processors.py — Penyuntik Data Global](#i3-context_processorspy--penyuntik-data-global)
- [I4. admin.py — Django Admin Panel](#i4-adminpy--django-admin-panel)
- [I5. Kesalahan Umum & Best Practice](#i5-kesalahan-umum--best-practice)

---

## A. Apa itu View?

**View** adalah fungsi atau class Python yang **menerima HTTP request dan mengembalikan HTTP response**.

### Analogi Restoran:
```
Penyewa (Browser)          Pelayan (VIEW)          Dapur (Database)
     │                           │                        │
     │── "Saya mau daftar menu" ─│                        │
     │   (GET /properti/list/)     │                        │
     │                           │── Query Properti ────────│
     │                           │                        │
     │                           │◄─ Data 50 properti ──────│
     │                           │                        │
     │                           │── Render template ──┐  │
     │                           │← HTML lengkap ──────┘  │
     │◄─ HTML Response ──────────│                        │
     │   (halaman daftar properti) │                        │
```

### Yang Terjadi di Balik Layar (10 Langkah):
```
1. Browser kirim: GET http://127.0.0.1:8000/properti/list/
2. Django terima request → cari URL yang cocok di config/urls.py
3. Match: path("properti/", include("apps.properti.urls"))
4. Django lanjut cari di apps/properti/urls.py
5. Match: path('list/', views.PropertiListView.as_view(), name='list')
6. Django panggil PropertiListView.as_view()() → return fungsi view
7. Fungsi view panggil dispatch() → cek method (GET/POST)
8. dispatch() panggil get() → proses request GET
9. get() ambil data dari database, render template
10. Return HttpResponse (HTML) → browser tampilkan halaman
```

---

## B. FBV vs CBV — Perbandingan Lengkap

### FBV (Function-Based View) — Cara Lama

**Apa itu FBV?**
FBV = View yang ditulis sebagai **FUNGSI Python biasa**. Ini cara paling dasar membuat view di Django.

```python
# ═══════════════════════════════════════════════════════════════
# CONTOH FBV — Daftar Properti (CARA LAMA)
# ═══════════════════════════════════════════════════════════════

from django.shortcuts import render, redirect, get_object_or_404
# ↑ render() = gabungkan template + data → HTML response
# ↑ redirect() = HTTP 302 redirect ke URL lain
# ↑ get_object_or_404() = ambil 1 objek, atau return 404 jika tidak ada

from django.contrib.auth.decorators import login_required
# ↑ Decorator: hanya user yang sudah login yang bisa akses
# Dari mana? django.contrib.auth (modul autentikasi bawaan Django)

from django.http import HttpResponse, JsonResponse, Http404
# ↑ HttpResponse = response HTTP mentah (bisa isi apa saja)
# ↑ JsonResponse = response berformat JSON (untuk AJAX/API)
# ↑ Http404 = exception untuk halaman tidak ditemukan

from apps.properti.models import Properti

@login_required
# ↑ DECORATOR — fungsi yang "membungkus" fungsi lain
# Cara kerja:
#   1. Cek request.user.is_authenticated
#   2. Jika True → lanjut jalankan fungsi di bawah
#   3. Jika False → redirect ke LOGIN_URL (default: /accounts/login/)
# Ini seperti "satpam" di depan pintu

def properti_list(request):
    """
    FBV untuk menampilkan daftar properti.
    
    Parameter:
    - request: objek HttpRequest dari Django
      Berisi: method, user, POST, GET, FILES, headers, session, dll
    
    Return: HttpResponse (HTML)
    """
    
    # ═══ CEK METHOD ═══
    # FBV harus cek method MANUAL
    if request.method != 'GET':
        return HttpResponse('Method not allowed', status=405)
    
    # ═══ CEK PERMISSION (MANUAL!) ═══
    if not request.user.is_staff:
        return redirect('login')
    
    # ═══ QUERY DATABASE ═══
    properti_list = Properti.objects.all().select_related('kategori', 'satuan')
    # .all() = ambil semua properti
    # .select_related() = JOIN tabel kategori & satuan (optimasi query)
    
    # ═══ SIAPKAN CONTEXT ═══
    context = {
        'properti_list': properti_list,
        'total': properti_list.count(),
    }
    
    # ═══ RENDER TEMPLATE ═══
    return render(request, 'properti/properti_list.html', context)
    # render() melakukan:
    # 1. Cari file templates/properti/properti_list.html
    # 2. Gabungkan template + context → HTML string
    # 3. Bungkus dalam HttpResponse → return


@login_required
def properti_create(request):
    """FBV untuk tambah properti baru."""
    
    if request.method == 'GET':
        # Tampilkan form kosong
        form = PropertiForm()
        return render(request, 'properti/properti_form.html', {'form': form})
    
    elif request.method == 'POST':
        # Proses form yang di-submit
        form = PropertiForm(request.POST, request.FILES)
        # request.POST = data form (nama, harga, dll)
        # request.FILES = file upload (gambar)
        
        if form.is_valid():
            properti = form.save(commit=False)
            # commit=False → buat objek TANPA simpan ke database
            # Kenapa? Karena kita mau set field tambahan dulu
            
            properti.dibuat_oleh = request.user
            properti.save()  # SEKARANG baru simpan ke database
            
            messages.success(request, 'Properti berhasil ditambahkan!')
            return redirect('properti:list')
        else:
            # Form tidak valid → tampilkan ulang form + error
            return render(request, 'properti/properti_form.html', {'form': form})


@login_required
def properti_update(request, pk):
    """FBV untuk edit properti. pk = primary key dari URL."""
    
    properti = get_object_or_404(Properti, pk=pk)
    # ↑ Cari properti dengan pk tertentu
    # Jika tidak ditemukan → otomatis return HTTP 404
    
    if request.method == 'GET':
        form = PropertiForm(instance=properti)
        # instance=properti → form terisi data properti yang ada
        return render(request, 'properti/properti_form.html', {'form': form})
    
    elif request.method == 'POST':
        form = PropertiForm(request.POST, request.FILES, instance=properti)
        if form.is_valid():
            form.save()
            messages.success(request, 'Properti berhasil diupdate!')
            return redirect('properti:list')
        return render(request, 'properti/properti_form.html', {'form': form})


@login_required
def properti_delete(request, pk):
    """FBV untuk hapus properti."""
    properti = get_object_or_404(Properti, pk=pk)
    
    if request.method == 'POST':  # Hanya POST yang boleh hapus (keamanan)
        nama = properti.nama
        properti.delete()
        return JsonResponse({'success': True, 'message': f'{nama} dihapus'})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
```

**Masalah FBV:**
```
1. KODE BERULANG — Setiap modul (properti, kategori, satuan, penyewa, 
   penyewa) harus tulis kode yang HAMPIR SAMA
2. PANJANG — 4 fungsi × 20+ baris = 80+ baris untuk 1 entitas
3. RAWAN ERROR — Cek permission manual, bisa lupa
4. TIDAK REUSABLE — Sulit berbagi logika antar view
```

---

### CBV (Class-Based View) — Cara Modern

**Apa itu CBV?**
CBV = View yang ditulis sebagai **CLASS Python**. Django menyediakan class siap pakai untuk operasi umum (CRUD).

```python
# ═══════════════════════════════════════════════════════════════
# CONTOH CBV — Daftar Properti (CARA MODERN — yang dipakai project)
# ═══════════════════════════════════════════════════════════════

from django.views.generic import ListView
# ↑ ListView = class CBV bawaan Django untuk menampilkan DAFTAR data
# Dari mana? django.views.generic (shipped bersama Django)
# "generic" = generik, bisa dipakai untuk model APAPUN

class PropertiListView(SubModulePermissionMixin, ListView):
    # ↑ class = mendefinisikan class baru
    # PropertiListView = nama class (konvensi: ModelName + Action + View)
    # (SubModulePermissionMixin, ListView) = INHERITANCE dari 2 class:
    #   1. SubModulePermissionMixin → menambah fitur cek permission
    #   2. ListView → semua logika menampilkan daftar data
    # Urutan PENTING! Mixin HARUS sebelum View (karena Python MRO)
    
    model = Properti
    # ↑ Model MANA yang datanya ditampilkan
    # Django otomatis: Properti.objects.all() → ambil semua properti
    
    template_name = 'properti/properti_list.html'
    # ↑ File template HTML — relatif ke folder templates/
    
    context_object_name = 'properti_list'
    # ↑ Nama variabel di template
    # Default Django: 'object_list' (kurang deskriptif)
    # Custom: 'properti_list' → {% for p in properti_list %}
    
    permission_module = 'properti'
    permission_sub_module = 'daftar_properti'
    permission_action = 'read'
    # ↑ 3 baris ini dari SubModulePermissionMixin
    # Django cek: apakah user login punya permission read di properti.daftar_properti?
    
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context
    # ↑ HANYA ini yang perlu ditulis!
    # SELESAI. Bandingkan dengan FBV yang 30+ baris
```

**Keuntungan CBV:**
```
1. SINGKAT — 15 baris vs 30+ baris FBV
2. DRY (Don't Repeat Yourself) — Logika CRUD sudah ada di Django
3. AMAN — Permission otomatis via mixin
4. KONSISTEN — Semua modul ikut pola yang sama
5. EXTENSIBLE — Bisa ditambah fitur via mixin tanpa ubah kode utama
```

> **📌 Mixin Permission CRUD:**
> Selain `SubModulePermissionMixin`, tersedia juga shorthand mixin per-aksi:
> `ReadPermissionMixin`, `CreatePermissionMixin`, `UpdatePermissionMixin`, `DeletePermissionMixin`.
> Lihat penjelasan lengkap di [07_SISTEM_PERMISSION_RBAC.md](07_SISTEM_PERMISSION_RBAC.md), section C.

### Tabel Perbandingan FBV vs CBV:

| Aspek | FBV | CBV |
|-------|-----|-----|
| Sintaks | `def view(request):` | `class MyView(ListView):` |
| Kode per CRUD | ~80 baris | ~40 baris |
| Cek method | Manual `if request.method` | Otomatis via `dispatch()` |
| Permission | Manual per fungsi | Mixin (1x tulis, pakai di semua) |
| Reusability | Copy-paste | Inheritance |
| URL registration | `path('url/', view)` | `path('url/', View.as_view())` |
| Digunakan di project | ❌ Tidak (kecuali API) | ✅ Ya, semua view |
| Cocok untuk | API sederhana, view unik | CRUD, halaman standar |

---

## C. Semua Jenis CBV Bawaan Django

Django menyediakan banyak CBV di `django.views.generic`. Berikut SEMUA jenis yang relevan:

### 1. `View` — Base Class (Paling Dasar)

```python
from django.views import View
# ↑ Class PALING DASAR — semua CBV mewarisi dari ini
# Tidak punya logika apapun, hanya kerangka kosong

class MyView(View):
    def get(self, request):
        """Dipanggil saat HTTP GET request."""
        return HttpResponse("Hello GET")
    
    def post(self, request):
        """Dipanggil saat HTTP POST request."""
        return HttpResponse("Hello POST")
    
    # Method lain yang bisa dioverride:
    # def put(self, request): ...
    # def patch(self, request): ...
    # def delete(self, request): ...
    # def head(self, request): ...
    # def options(self, request): ...

# Kapan pakai? Jarang — hanya jika tidak ada CBV yang cocok
```

### 2. `TemplateView` — Tampilkan Halaman Statis

```python
from django.views.generic import TemplateView
# ↑ TemplateView = render template TANPA query database
# Cocok untuk: halaman statis, about, help, dashboard sederhana

class HalamanBantuanView(TemplateView):
    template_name = 'bantuan.html'
    # SELESAI! Django otomatis render templates/bantuan.html
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['judul'] = 'Halaman Bantuan'
        return context
    # ↑ OPSIONAL — jika perlu kirim data ke template

# Digunakan di project: PropertiImportView (halaman upload file)
```

### 3. `ListView` — Tampilkan DAFTAR Data

```python
from django.views.generic import ListView
# ↑ ListView = query SEMUA data dari model, kirim ke template sebagai list
# Digunakan di: KategoriListView, SatuanListView, PropertiListView,
#   PenyewaListView, PenyewaListView, PropertiListView, dll

class KategoriListView(SubModulePermissionMixin, ListView):
    model = Kategori
    # Django otomatis: Kategori.objects.all()
    
    template_name = 'properti/kategori_list.html'
    context_object_name = 'kategori_list'  # Default: 'object_list'
    
    # ═══ METHOD YANG BISA DI-OVERRIDE ═══
    
    def get_queryset(self):
        """
        Override queryset — filter/sort/optimize data.
        DEFAULT: self.model.objects.all()
        """
        # Contoh: hanya tampilkan yang aktif, urutkan A-Z
        return Kategori.objects.filter(aktif=True).order_by('nama')
    
    def get_context_data(self, **kwargs):
        """
        Tambahkan data ekstra ke context template.
        DEFAULT: {'object_list': queryset, 'paginator': ..., 'page_obj': ...}
        """
        context = super().get_context_data(**kwargs)
        context['total_kategori'] = self.get_queryset().count()
        return context
    
    paginate_by = 25
    # ↑ OPSIONAL — aktifkan pagination (25 per halaman)
    # Django otomatis membuat paginator + page_obj di context
    # Template: {% for p in page_obj %} ... {% endfor %}
    
    ordering = ['-dibuat_pada']
    # ↑ OPSIONAL — default sorting (- = descending)
```

**Method Lifecycle ListView (urutan pemanggilan):**
```
Browser GET /properti/kategori/
    │
    ▼
1. as_view()          → Konversi class jadi callable function
    │
    ▼
2. dispatch()         → Cek HTTP method → panggil get() untuk GET
    │
    ▼
3. get()              → Orchestrator utama
    │
    ├── get_queryset()     → Ambil data dari database
    │
    ├── get_context_data() → Siapkan context dict
    │      │
    │      └── get_paginator() → Buat paginator (jika paginate_by)
    │
    └── render_to_response() → Render template + context → HttpResponse
           │
           └── get_template_names() → Tentukan template mana
```

### 4. `DetailView` — Tampilkan DETAIL 1 Data

```python
from django.views.generic import DetailView
# ↑ DetailView = query 1 objek berdasarkan pk/slug, tampilkan detail
# Digunakan di: TagihanDetailView

class PropertiDetailView(DetailView):
    model = Properti
    template_name = 'properti/properti_detail.html'
    context_object_name = 'properti'  # Default: 'object'
    
    # Django otomatis: Properti.objects.get(pk=<pk dari URL>)
    # Jika tidak ditemukan → HTTP 404

    # ═══ METHOD YANG BISA DI-OVERRIDE ═══
    
    def get_object(self, queryset=None):
        """Override cara mengambil objek."""
        # Default: self.model.objects.get(pk=self.kwargs['pk'])
        obj = super().get_object(queryset)
        obj.view_count += 1  # Contoh: hitung jumlah view
        obj.save()
        return obj
```

### 5. `CreateView` — Form TAMBAH Data Baru

```python
from django.views.generic import CreateView
# ↑ CreateView = tampilkan form kosong (GET), proses submit (POST)
# Digunakan di: KategoriCreateView, PropertiCreateView, dll

class KategoriCreateView(SubModulePermissionMixin, CreateView):
    model = Kategori
    
    fields = ['nama', 'deskripsi']
    # ↑ OPSI 1: Daftar field → Django buat form sederhana otomatis
    # ATAU
    # form_class = KategoriForm
    # ↑ OPSI 2: Pakai form class custom (jika perlu widget/validasi khusus)
    # PILIH SALAH SATU — tidak boleh dua-duanya!
    
    template_name = 'properti/kategori_form.html'
    
    success_url = reverse_lazy('properti:kategori')
    # ↑ URL redirect SETELAH data berhasil disimpan
    # reverse_lazy() vs reverse():
    #   reverse() → langsung resolve URL → ERROR jika URL belum ready
    #   reverse_lazy() → resolve URL saat DIBUTUHKAN → aman di class attribute
    # SELALU pakai reverse_lazy() di class attribute!
    
    # ═══ METHOD YANG BISA DI-OVERRIDE ═══
    
    def form_valid(self, form):
        """
        Dipanggil OTOMATIS saat form VALID (semua validasi OK).
        
        Apa yang terjadi di dalam (default):
        1. form.save() → simpan ke database (INSERT SQL)
        2. redirect ke success_url
        
        Kita override untuk:
        - Set field tambahan (dibuat_oleh)
        - Kirim notifikasi
        - Log aktivitas
        """
        form.instance.dibuat_oleh = self.request.user
        # form.instance = objek Kategori yang BELUM disimpan
        # self.request.user = user yang sedang login
        
        messages.success(self.request, 'Kategori berhasil ditambahkan')
        return super().form_valid(form)
        # ↑ Panggil parent → simpan ke DB + redirect
    
    def form_invalid(self, form):
        """
        Dipanggil OTOMATIS saat form INVALID.
        
        Default: render ulang form dengan pesan error
        Data yang sudah diisi TETAP ADA (tidak hilang)
        """
        messages.error(self.request, 'Data tidak valid!')
        return super().form_invalid(form)
    
    def get_initial(self):
        """
        Data awal form (pre-fill).
        Return dictionary field_name: default_value
        """
        return {'aktif': True}  # Checkbox aktif ter-centang by default
    
    def get_form_kwargs(self):
        """
        Argumen yang dikirim ke constructor form.
        Berguna untuk mengirim data tambahan ke form.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Kirim user ke form
        return kwargs
```

**Method Lifecycle CreateView:**
```
═══ GET REQUEST (tampilkan form kosong) ═══

1. dispatch()     → HTTP method = GET → panggil get()
2. get()
   ├── get_form_class()      → tentukan form class
   ├── get_form()             → buat instance form (kosong)
   │     └── get_form_kwargs() → {'initial': ..., 'prefix': ...}
   │     └── get_initial()     → data awal form
   └── render_to_response()   → render template + form → HTML

═══ POST REQUEST (proses form yang di-submit) ═══

1. dispatch()     → HTTP method = POST → panggil post()
2. post()
   ├── get_form_class()      → tentukan form class
   ├── get_form()             → buat instance form DENGAN data POST
   │     └── get_form_kwargs() → {'data': POST, 'files': FILES, ...}
   ├── form.is_valid()        → validasi semua field
   │
   ├── [VALID] form_valid()   → simpan + redirect
   │     ├── form.save()      → INSERT INTO database
   │     └── redirect(success_url)
   │
   └── [INVALID] form_invalid() → render ulang + error messages
```

### 6. `UpdateView` — Form EDIT Data yang Ada

```python
from django.views.generic import UpdateView
# ↑ UpdateView = SAMA seperti CreateView, tapi form TERISI data yang ada
# Perbedaan dengan CreateView:
#   - Butuh pk di URL untuk mengambil objek
#   - Form pre-filled dengan data existing
#   - form.save() → UPDATE (bukan INSERT)

class KategoriUpdateView(SubModulePermissionMixin, UpdateView):
    model = Kategori
    fields = ['nama', 'deskripsi']
    template_name = 'properti/kategori_form.html'  # BISA pakai template SAMA
    success_url = reverse_lazy('properti:kategori')
    
    # URL: /properti/kategori/<int:pk>/edit/
    # Django otomatis: Kategori.objects.get(pk=<pk>)
    # Form terisi: nama="Makanan", deskripsi="Kategori makanan"
    
    # Method tambahan yang berguna:
    
    def get_object(self, queryset=None):
        """Override cara mengambil objek yang akan diedit."""
        obj = super().get_object(queryset)
        # Contoh: cek apakah user boleh edit objek INI
        if obj.dibuat_oleh != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return obj
```

### 7. `DeleteView` — Hapus Data

```python
from django.views.generic import DeleteView
# ↑ DeleteView = tampilkan konfirmasi (GET), hapus data (POST/DELETE)
# Di project ini: SEMUA delete via AJAX (return JSON, bukan HTML)

class KategoriDeleteView(SubModulePermissionMixin, DeleteView):
    model = Kategori
    success_url = reverse_lazy('properti:kategori')
    
    def delete(self, request, *args, **kwargs):
        """
        Override delete() untuk return JSON (bukan redirect HTML).
        
        Kenapa JSON bukan HTML?
        - Frontend pakai AJAX (JavaScript fetch/jQuery.ajax)
        - Tidak perlu reload halaman → UX lebih cepat
        - JavaScript tampilkan toast notification
        """
        self.object = self.get_object()
        # ↑ self.get_object() → Kategori.objects.get(pk=<pk>)
        # self.object = objek Kategori yang akan dihapus
        
        try:
            nama = self.object.nama  # Simpan nama sebelum dihapus
            self.object.delete()     # DELETE FROM kategori WHERE id=<pk>
            
            return JsonResponse({
                'success': True,
                'message': f'Kategori {nama} berhasil dihapus'
            })
            # Output: {"success": true, "message": "Kategori Makanan berhasil dihapus"}
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Gagal menghapus: {str(e)}'
            }, status=400)
            # Contoh error: ProtectedError jika ada properti yang pakai kategori ini
```

### 8. CBV Lainnya (Tidak Dipakai di Project, Tapi Perlu Diketahui)

```python
# ─── FormView ───
from django.views.generic import FormView
# FormView = form yang TIDAK terikat model (bukan ModelForm)
# Contoh: form kontak, form pencarian, form login custom
class ContactView(FormView):
    form_class = ContactForm
    template_name = 'contact.html'
    success_url = '/thank-you/'
    
    def form_valid(self, form):
        # Tidak save ke database, tapi kirim email
        send_email(form.cleaned_data)
        return super().form_valid(form)

# ─── RedirectView ───
from django.views.generic import RedirectView
# RedirectView = redirect ke URL lain (HTTP 301/302)
class OldProductView(RedirectView):
    url = '/properti/list/'   # Redirect semua akses ke URL baru
    permanent = True         # HTTP 301 (permanent redirect)

# ─── ArchiveView, DateView, dll ───
# Untuk blog/arsip berdasarkan tanggal — tidak dipakai di SIMKOS
```

---

## D. Struktur Internal CBV — Method Lifecycle LENGKAP

### Diagram Seluruh Method yang Ada di CBV:

```
                        View (Base)
                          │
            ┌─────────────┼─────────────┐
            │             │             │
      TemplateView    ListView     FormView
            │             │             │
            │         DetailView   CreateView
            │                     UpdateView
            │                     DeleteView
```

### Semua Method/Attribute di ListView (Lengkap):

```python
class ListView:
    # ═══ ATTRIBUTES (CLASS VARIABLE) ═══
    model = None                    # Model class (wajib)
    queryset = None                 # QuerySet custom (alternatif model)
    template_name = None            # Path template
    template_name_suffix = '_list'  # Suffix auto-template: 'properti/properti_list.html'
    context_object_name = None      # Nama context (default: 'object_list')
    paginate_by = None              # Jumlah per halaman (None = no pagination)
    paginate_orphans = 0            # Min item di halaman terakhir
    ordering = None                 # Default sort: ['-created'] atau ['nama']
    allow_empty = True              # Boleh tampil jika 0 data?
    content_type = None             # Response content type (default: text/html)
    extra_context = None            # Context tambahan (dict)
    
    # ═══ METHODS — Urutan Pemanggilan ═══
    
    # LEVEL 1: Entry Point
    @classmethod
    def as_view(cls, **initkwargs):
        """Mengubah class jadi callable function untuk URL config."""
        # cls = class itu sendiri (KategoriListView)
        # Return: fungsi view(request) yang bisa dipanggil Django
    
    def setup(self, request, *args, **kwargs):
        """Inisialisasi attribute instance (self.request, self.args, self.kwargs)."""
    
    def dispatch(self, request, *args, **kwargs):
        """Router — cek HTTP method, panggil get/post/put/delete yang sesuai."""
    
    # LEVEL 2: HTTP Method Handler
    def get(self, request, *args, **kwargs):
        """Handler untuk GET request — orkestrator utama."""
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return self.render_to_response(context)
    
    # LEVEL 3: Data
    def get_queryset(self):
        """Ambil data dari database. Default: model.objects.all()"""
    
    def get_ordering(self):
        """Tentukan ordering. Default: self.ordering"""
    
    # LEVEL 4: Context
    def get_context_data(self, **kwargs):
        """Siapkan dictionary context untuk template."""
    
    def get_context_object_name(self, object_list):
        """Tentukan nama context. Default: model_name + '_list'"""
    
    # LEVEL 5: Pagination
    def get_paginate_by(self, queryset):
        """Tentukan jumlah item per halaman."""
    
    def get_paginator(self, queryset, per_page, **kwargs):
        """Buat objek Paginator."""
    
    def paginate_queryset(self, queryset, page_size):
        """Lakukan pagination, return (paginator, page, object_list, is_paginated)."""
    
    # LEVEL 6: Rendering
    def render_to_response(self, context, **kwargs):
        """Render template + context → HttpResponse."""
    
    def get_template_names(self):
        """Tentukan template mana yang dipakai. Default: app/model_list.html"""
```

### Semua Method di CreateView (Lengkap):

```python
class CreateView:
    # ═══ ATTRIBUTES ═══
    model = None
    form_class = None           # Custom form class
    fields = None               # Field untuk auto-generated form
    template_name = None
    template_name_suffix = '_form'
    success_url = None          # URL redirect setelah berhasil
    initial = {}                # Data awal form
    prefix = None               # Prefix untuk field name HTML
    
    # ═══ METHODS ═══
    
    # Form
    def get_form_class(self):
        """Tentukan class form. Pilih form_class atau auto dari fields."""
    
    def get_form(self, form_class=None):
        """Buat instance form."""
    
    def get_form_kwargs(self):
        """Argumen untuk constructor form.
        GET: {'initial': ..., 'prefix': ...}
        POST: {'initial': ..., 'prefix': ..., 'data': POST, 'files': FILES}
        """
    
    def get_initial(self):
        """Data awal form (pre-fill). Return dict."""
    
    def get_prefix(self):
        """Prefix field name. Default: None."""
    
    # Validasi
    def form_valid(self, form):
        """Form VALID → save + redirect. OVERRIDE INI!"""
    
    def form_invalid(self, form):
        """Form INVALID → render ulang + errors."""
    
    # URL
    def get_success_url(self):
        """URL redirect setelah sukses. Override jika dinamis."""
```

---

## E. Mixin — Menambah Fitur ke View

### Apa itu Mixin?

**Mixin** = class yang **TIDAK berdiri sendiri**, tapi dicampur (mixed-in) ke class lain untuk menambah fitur.

**Analogi:** 
- View = kopi
- Mixin = gula, susu, creamer
- Kopi bisa diminum tanpa gula (view tanpa mixin)
- Kopi + gula + susu = kopi susu manis (view + permission + logging)

### Mixin yang Ada di Project (`apps/core/mixins.py`):

| Mixin | Fungsi | Cek apa | Digunakan di |
|-------|--------|---------|-------------|
| `SubModulePermissionMixin` | Cek permission modul + sub-modul | `has_permission(user, module, action, sub_module)` | **SEMUA view** |
| `ModulePermissionMixin` | Cek permission level modul saja | `has_permission(user, module, action)` | View tanpa sub-modul |
| `ReadPermissionMixin` | Cek permission baca | `can_view` | ListView |
| `CreatePermissionMixin` | Cek permission tambah | `can_create` | CreateView |
| `UpdatePermissionMixin` | Cek permission edit | `can_edit` | UpdateView |
| `DeletePermissionMixin` | Cek permission hapus | `can_delete` | DeleteView |
| `AdminOrSuperuserMixin` | Hanya admin/superuser | `is_staff` atau `is_superuser` | Legacy (lama) |
| `SuperuserRequiredMixin` | Hanya superuser | `is_superuser` | Legacy (lama) |

### Cara Kerja SubModulePermissionMixin (Detail):

```python
class SubModulePermissionMixin:
    permission_module = None       # WAJIB diisi: 'properti', 'sewa', dll
    permission_sub_module = None   # OPSIONAL: 'kategori', 'satuan'
    permission_action = 'read'     # 'read'/'create'/'write'/'delete'
    
    def dispatch(self, request, *args, **kwargs):
        # LANGKAH 1: Ambil user dari request
        user = request.user
        
        # LANGKAH 2: Cek apakah punya permission
        allowed = has_permission(
            user,
            self.permission_module,      # 'properti'
            self.permission_action,      # 'read'
            self.permission_sub_module   # 'kategori'
        )
        # Di dalam has_permission():
        #   - Cek user.is_authenticated (sudah login?)
        #   - Ambil profile.role ('ADMIN', 'KASIR', dll)
        #   - Jika SUPERUSER → return True (bypass semua)
        #   - Query: RolePermission.objects.get(role='ADMIN', 
        #            module='properti', sub_module='kategori')
        #   - Return: perm.can_view / can_create / can_edit / can_delete
        
        # LANGKAH 3: Tolak jika tidak punya permission
        if not allowed:
            raise PermissionDenied  # → 403 Forbidden page
        
        # LANGKAH 4: Lanjut ke view asli (ListView.dispatch → get/post)
        return super().dispatch(request, *args, **kwargs)
```

### Python MRO (Method Resolution Order) — Kenapa Urutan Inheritance Penting?

```python
# ═══ BENAR ═══
class KategoriListView(SubModulePermissionMixin, ListView):
    pass

# Python MRO: 
# KategoriListView → SubModulePermissionMixin → ListView → View
# Saat dispatch() dipanggil:
# 1. Python cari dispatch() di KategoriListView → TIDAK ADA
# 2. Python cari di SubModulePermissionMixin → ADA! → cek permission
# 3. super().dispatch() → Python cari di ListView → ADA! → proses request
# ✅ Permission dicek SEBELUM view dijalankan

# ═══ SALAH ═══
class KategoriListView(ListView, SubModulePermissionMixin):
    pass

# Python MRO: 
# KategoriListView → ListView → SubModulePermissionMixin → View
# Saat dispatch() dipanggil:
# 1. Python cari dispatch() di KategoriListView → TIDAK ADA
# 2. Python cari di ListView → ADA! → langsung proses request
# ❌ Permission TIDAK pernah dicek! Mixin di-SKIP!
```

---

## F. URL Routing — Detail Lengkap

### Struktur URL 2 Level:

```
config/urls.py (LEVEL 1 — Root URL)
    │
    ├── path("properti/", include("apps.properti.urls"))
    │         │
    │         └── apps/properti/urls.py (LEVEL 2 — App URL)
    │               ├── path('kategori/', KategoriListView)
    │               ├── path('kategori/add/', KategoriCreateView)
    │               └── path('list/', PropertiListView)
    │
    ├── path("sewa/", include("apps.sewa.urls"))
    │         │
    │         └── apps/sewa/urls.py (LEVEL 2)
    │               ├── path('penyewa/', PenyewaListView)
    │               └── path('tagihan/', TagihanListView)
    │
    └── ... (modul lainnya)

Hasil URL final:
/properti/kategori/          → KategoriListView
/properti/kategori/add/      → KategoriCreateView
/properti/list/              → PropertiListView
/sewa/penyewa/       → PenyewaListView
/sewa/tagihan/    → TagihanListView
```

### File `config/urls.py` — Penjelasan Lengkap:

```python
from django.urls import include, path
# ↑ path() = mendaftarkan 1 URL pattern
# ↑ include() = menyertakan URL dari file lain

from django.conf import settings
from django.conf.urls.static import static
# ↑ Untuk serve file media (gambar upload) di development

urlpatterns = [
    # ═══ API ═══
    path("api/search/", global_search_api, name='global_search'),
    # ↑ FBV — satu-satunya FBV di URL utama
    # Endpoint pencarian global: /api/search/?q=beras
    # Dipanggil via AJAX dari navbar search box
    # Return JSON: {results: [{title: 'Beras', url: '/properti/', ...}]}
    
    # ═══ AUTH ═══
    path("", include("auth.urls")),
    # ↑ Login, register, forgot password, logout
    # "" = root URL — auth tidak punya prefix
    # /login/, /register/, /forgot-password/
    
    # ═══ SIMKOS MODULES ═══
    path("", include("apps.dashboard.urls")),            # / (root)
    path("users/", include("apps.user_management.urls")), # /users/...
    path("properti/", include("apps.properti.urls")),         # /properti/...
    path("sewa/", include("apps.sewa.urls")),   # /sewa/...
    path("penyewa/", include("apps.penyewa.urls")),   # /penyewa/...
    path("sewa/", include("apps.sewa.urls")),   # /sewa/...
    path("pos/", include("apps.sewa.urls")),               # /pos/...
    path("biaya/", include("apps.biaya.urls")),           # /biaya/...
    path("laporan/", include("apps.laporan.urls")),       # /laporan/...
    path("activity-log/", include("apps.activity_log.urls")),
    path("pengaturan/", include("apps.pengaturan.urls")), # /pengaturan/...
    path("access/", include("apps.permission_management.urls")),
    path("hr/", include("apps.hr.urls")),                 # /hr/...
    path("automation/", include("apps.automation.urls")), # /automation/...
]

# Serve media files (HANYA saat DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # MEDIA_URL = '/media/'
    # MEDIA_ROOT = 'd:/SIMKOS-Software/media/'
    # Jadi /media/properti/beras.jpg → serve file dari media/properti/beras.jpg

# Custom Error Handlers
handler404 = custom_error_404   # Halaman 404 custom (bukan default Django)
handler403 = custom_error_403   # Halaman 403 custom
handler400 = custom_error_400
handler500 = custom_error_500
```

### File `apps/properti/urls.py` — Penjelasan:

```python
from django.urls import path
from . import views
# ↑ "." = import dari folder yang sama (apps/properti/)
# Artinya: from apps.properti import views

app_name = 'properti'
# ↑ NAMESPACE — sangat penting!
# Tanpa namespace: {% url 'list' %} → bisa bentrok (properti & sewa punya 'list')
# Dengan namespace: {% url 'properti:list' %} → PASTI ke /properti/list/

urlpatterns = [
    # ═══ KATEGORI (SubCRUD) ═══
    path('kategori/', views.KategoriListView.as_view(), name='kategori'),
    # URL final: /properti/kategori/  (prefix "properti/" dari config/urls.py + "kategori/")
    # .as_view() = konversi CBV class → fungsi view callable
    # name='kategori' → nama unik URL → {% url 'properti:kategori' %}
    
    path('kategori/add/', views.KategoriCreateView.as_view(), name='kategori_add'),
    # URL final: /properti/kategori/add/
    
    path('kategori/<int:pk>/edit/', views.KategoriUpdateView.as_view(), name='kategori_edit'),
    # URL final: /properti/kategori/5/edit/
    # <int:pk> = URL CONVERTER:
    #   <    > = tanda variabel dinamis
    #   int    = tipe data (harus integer)
    #   pk     = nama parameter (diterima view via self.kwargs['pk'])
    #
    # Jenis converter yang tersedia:
    #   <int:pk>    → integer: 1, 42, 100       → /kategori/42/edit/
    #   <str:slug>  → string tanpa /: "beras"   → /properti/beras/
    #   <slug:slug> → slug: "beras-premium"     → /properti/beras-premium/
    #   <uuid:id>   → UUID: "075194d3-..."      → /properti/075194d3-.../
    #   <path:rest> → path dengan /             → /files/folder/sub/file.txt
    
    path('kategori/<int:pk>/delete/', views.KategoriDeleteView.as_view(), name='kategori_delete'),
    
    # ═══ SATUAN (SubCRUD) ═══
    path('satuan/', views.SatuanListView.as_view(), name='satuan'),
    path('satuan/add/', views.SatuanCreateView.as_view(), name='satuan_add'),
    path('satuan/<int:pk>/edit/', views.SatuanUpdateView.as_view(), name='satuan_edit'),
    path('satuan/<int:pk>/delete/', views.SatuanDeleteView.as_view(), name='satuan_delete'),
    
    # ═══ PROPERTI (CRUD Utama) ═══
    path('list/', views.PropertiListView.as_view(), name='list'),
    path('tambah/', views.PropertiCreateView.as_view(), name='tambah'),
    path('import/', views.PropertiImportView.as_view(), name='import'),
    path('<int:pk>/edit/', views.PropertiUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.PropertiDeleteView.as_view(), name='delete'),
]
```

### Cara Menggunakan URL di Template dan Python:

```html
<!-- ═══ DI TEMPLATE (HTML) ═══ -->

<!-- 1. Link biasa (tanpa parameter) -->
<a href="{% url 'properti:kategori' %}">Daftar Kategori</a>
<!-- Output: <a href="/properti/kategori/">Daftar Kategori</a> -->

<!-- 2. Link dengan parameter pk -->
<a href="{% url 'properti:kategori_edit' pk=k.pk %}">Edit</a>
<!-- Output: <a href="/properti/kategori/5/edit/">Edit</a> -->

<!-- 3. Di JavaScript (AJAX delete) -->
<script>
const url = `/properti/kategori/${id}/delete/`;
// Atau: `{% url 'properti:kategori_delete' pk=0 %}`.replace('0', id)
</script>
```

```python
# ═══ DI PYTHON (views.py) ═══

from django.urls import reverse, reverse_lazy

# reverse() — evaluasi LANGSUNG (untuk di dalam method)
url = reverse('properti:kategori_edit', kwargs={'pk': 5})
# Hasil: '/properti/kategori/5/edit/'

# reverse_lazy() — evaluasi NANTI (untuk class attribute)
success_url = reverse_lazy('properti:kategori')
# Hasil (saat diakses): '/properti/kategori/'

# redirect() — shortcut untuk HttpResponseRedirect
from django.shortcuts import redirect
return redirect('properti:list')  # Redirect ke /properti/list/
```

---

## G. TemplateLayout — Custom Layout System

### Apa itu TemplateLayout dan Kenapa WAJIB?

```python
# File: web_project/__init__.py

class TemplateLayout:
    """
    Class CUSTOM project ini (BUKAN bawaan Django).
    Menginisialisasi konfigurasi layout Sneat Bootstrap 5.
    
    Kenapa ada?
    - Theme Sneat punya banyak konfigurasi (sidebar, navbar, theme, dll)
    - Semua halaman HARUS punya konfigurasi ini agar layout benar
    - Tanpa ini: sidebar tidak muncul, theme rusak, menu hilang
    """
    
    @staticmethod
    def init(view, context):
        """
        WAJIB dipanggil di setiap get_context_data().
        
        Apa yang dilakukan:
        1. Baca config/template.py → ambil semua konfigurasi
        2. Tambahkan ke context:
           - layout_path: 'layout/master.html'
           - content_layout: 'compact'
           - navbar_type: 'fixed'
           - is_menu: True
           - style: 'light' atau 'dark'
           - (banyak lagi)
        3. Baca vertical_menu.json → data menu sidebar
        4. Tentukan CSS class berdasarkan konfigurasi
        
        Parameter:
        - view: instance view yang memanggil (self)
        - context: dictionary context yang sudah ada
        
        Return: context yang sudah ditambahkan data layout
        """
        context = TemplateLayout.set_layout(view, context)
        return context
```

### Pola Penggunaan Standar (SEMUA view harus ikuti):

```python
class AnyListView(SubModulePermissionMixin, ListView):
    model = AnyModel
    template_name = 'path/template.html'
    # ...
    
    def get_context_data(self, **kwargs):
        # POLA WAJIB:
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        # super().get_context_data(**kwargs) = context dari parent (ListView)
        #   Berisi: 'object_list' (atau nama custom), paginator, dll
        # TemplateLayout.init() = TAMBAHKAN data layout ke context
        #   Berisi: layout_path, sidebar data, theme config, dll
        
        # Tambah data custom SETELAH TemplateLayout.init()
        context['tambahan'] = 'data custom'
        
        return context
```

---

## H. Contoh Nyata dari Project — View dengan Logika Bisnis

### PropertiCreateView — Handle Kamar Awal:

```python
class PropertiCreateView(SubModulePermissionMixin, CreateView):
    model = Properti
    form_class = PropertiForm     # Custom form (bukan fields=[])
    template_name = 'properti/properti_form.html'
    success_url = reverse_lazy('properti:list')
    permission_module = 'properti'
    permission_sub_module = 'tambah_properti'
    permission_action = 'create'
    
    def form_valid(self, form):
        # LANGKAH 1: Set pembuat
        form.instance.dibuat_oleh = self.request.user
        
        # LANGKAH 2: Simpan properti (parent form_valid → INSERT)
        response = super().form_valid(form)
        
        # LANGKAH 3: Handle kamar awal (field BUKAN dari model)
        kamar_awal = self.request.POST.get('kamar_awal')
        # ↑ 'kamar_awal' adalah input TAMBAHAN di HTML form
        # BUKAN field di model Properti — makanya diambil dari request.POST
        
        if kamar_awal and float(kamar_awal) > 0:
            properti = form.instance.cabang  # Properti yang dipilih
            if not properti:
                properti = Properti.objects.filter(aktif=True).first()
                if not properti:
                    properti = Properti.objects.create(
                        kode='GD-DEFAULT', nama='Properti Utama', aktif=True
                    )
                    # ↑ Auto-create properti default jika belum ada
            
            Kamar.objects.update_or_create(
                properti=form.instance,   # Properti yang baru dibuat
                properti=properti,          # Properti tujuan
                defaults={'jumlah': float(kamar_awal)}
                # update_or_create():
                # - Cari Kamar dengan properti+properti
                # - Jika ADA → UPDATE jumlah
                # - Jika TIDAK ADA → CREATE baru
            )
        
        messages.success(self.request, 'Properti berhasil ditambahkan')
        return response
```

### PropertiListView — Optimasi Query (N+1 Problem):

```python
class PropertiListView(SubModulePermissionMixin, ListView):
    # ...
    
    def get_queryset(self):
        return Properti.objects.prefetch_related(
            'kamar_set',           # Ambil semua kamar terkait
            'kamar_set__properti'    # Ambil properti dari setiap kamar
        ).select_related(
            'kategori',           # JOIN kategori (1 query)
            'satuan',             # JOIN satuan (1 query)
            'cabang'              # JOIN properti cabang (1 query)
        )
        # TANPA optimasi (N+1 Problem):
        # Query 1: SELECT * FROM properti (50 properti)
        # Query 2: SELECT * FROM kategori WHERE id=1 (untuk properti 1)
        # Query 3: SELECT * FROM kategori WHERE id=2 (untuk properti 2)
        # ... 50 query lagi untuk kamar, satuan, properti
        # TOTAL: 150+ query (LAMBAT!)
        
        # DENGAN optimasi:
        # Query 1: SELECT * FROM properti JOIN kategori JOIN satuan JOIN properti
        # Query 2: SELECT * FROM kamar WHERE properti_id IN (1,2,3,...,50)
        # Query 3: SELECT * FROM properti WHERE id IN (...)
        # TOTAL: 3 query (CEPAT!)
    
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        properti_list = context['properti_list']
        
        # Hitung total untuk summary/export
        total_properti = 0
        total_kamar = 0
        total_nilai_beli = 0
        total_nilai_jual = 0
        
        for properti in properti_list:
            total_properti += 1
            kamar = properti.total_kamar_total      # @property — hitung dari kamar_set
            total_kamar += kamar
            total_nilai_beli += kamar.harga_bulanan_beli * kamar
            total_nilai_jual += properti.harga * kamar
        
        context['total_properti'] = total_properti          # 50
        context['total_kamar'] = total_kamar              # 2500
        context['total_nilai_beli'] = total_nilai_beli  # Rp 37.500.000
        context['total_nilai_jual'] = total_nilai_jual  # Rp 50.000.000
        
        context['properti_list'] = Properti.objects.filter(aktif=True)
        return context
```

### PropertiImportView — TemplateView dengan POST:

```python
class PropertiImportView(SubModulePermissionMixin, TemplateView):
    """
    TemplateView + override post() = hybrid view.
    
    Kenapa TemplateView bukan CreateView?
    Karena TIDAK membuat 1 properti — tapi import BANYAK properti dari file.
    CreateView designed untuk 1 objek. Import = custom logic.
    """
    template_name = 'properti/properti_import.html'
    
    def post(self, request, *args, **kwargs):
        """
        Proses upload file CSV/Excel.
        TemplateView TIDAK punya post() default → kita BUAT sendiri.
        
        Alur:
        1. Validasi file (ada? format benar?)
        2. Parse file (CSV → csv.DictReader, Excel → BeautifulSoup)
        3. Loop setiap baris → buat/cari Kategori, Satuan → buat Properti
        4. Return summary (berapa berhasil, berapa gagal)
        """
        # ... (lihat apps/properti/views.py untuk kode lengkap)
```

---

## I. Ringkasan Semua View di Project

| Modul | View Class | Tipe | URL |
|-------|-----------|------|-----|
| **Properti** | KategoriListView | ListView | /properti/kategori/ |
| | KategoriCreateView | CreateView | /properti/kategori/add/ |
| | KategoriUpdateView | UpdateView | /properti/kategori/\<pk\>/edit/ |
| | KategoriDeleteView | DeleteView | /properti/kategori/\<pk\>/delete/ |
| | SatuanListView | ListView | /properti/satuan/ |
| | SatuanCreateView | CreateView | /properti/satuan/add/ |
| | SatuanUpdateView | UpdateView | /properti/satuan/\<pk\>/edit/ |
| | SatuanDeleteView | DeleteView | /properti/satuan/\<pk\>/delete/ |
| | PropertiListView | ListView | /properti/list/ |
| | PropertiCreateView | CreateView | /properti/tambah/ |
| | PropertiUpdateView | UpdateView | /properti/\<pk\>/edit/ |
| | PropertiDeleteView | DeleteView | /properti/\<pk\>/delete/ |
| | PropertiImportView | TemplateView | /properti/import/ |
| **Sewa** | PenyewaListView | ListView | /sewa/penyewa/ |
| | PenyewaCreateView | CreateView | /sewa/penyewa/add/ |
| | TagihanListView | ListView | /sewa/tagihan/ |
| | TagihanCreateView | CreateView | /sewa/tagihan/add/ |
| | TagihanDetailView | DetailView | /sewa/tagihan/\<pk\>/ |
| **Dashboard** | DashboardView | TemplateView | / |
| **POS** | POSView | TemplateView | /pos/ |

---

## F2. path() vs re_path() — Deep Dive

### Apa Bedanya?

| Aspek | `path()` | `re_path()` |
|-------|----------|-------------|
| Import | `from django.urls import path` | `from django.urls import re_path` |
| Syntax | Converter bawaan `<int:pk>` | Regex Python `(?P<pk>\d+)` |
| Mudah dibaca | ✅ Ya | ❌ Lebih kompleks |
| Fleksibilitas | Terbatas (5 converter) | Tak terbatas (regex apapun) |
| Dipakai di project | ✅ Semua URL | ❌ Tidak dipakai |
| Direkomendasikan | ✅ Ya (Django 2.0+) | Hanya jika path() tidak cukup |

### Contoh Perbandingan:

```python
from django.urls import path, re_path

# ═══ SAMA PERSIS hasilnya: ═══

# path() — mudah dibaca
path('kategori/<int:pk>/edit/', KategoriUpdateView.as_view())

# re_path() — regex (lama)
re_path(r'^kategori/(?P<pk>\d+)/edit/$', KategoriUpdateView.as_view())

# ═══ KAPAN re_path() diperlukan? ═══
# Ketika URL perlu pattern yang TIDAK bisa di-handle path()

# Contoh: URL dengan format tanggal (YYYY/MM/DD)
re_path(
    r'^laporan/(?P<tahun>\d{4})/(?P<bulan>\d{2})/$',
    LaporanBulananView.as_view()
)
# Match: /laporan/2026/02/  → kwargs={'tahun': '2026', 'bulan': '02'}
# path() tidak bisa handle pattern \d{4} (exactly 4 digits)
```

### 5 URL Converter Bawaan Django (untuk path()):

```python
# 1. <int:pk> — Integer positif
path('properti/<int:pk>/', ...)
# Match: /properti/42/     ✅
# No match: /properti/abc/  ❌ (bukan integer)
# No match: /properti/-1/   ❌ (negatif)

# 2. <str:nama> — String (tanpa /)
path('properti/<str:nama>/', ...)
# Match: /properti/beras/   ✅
# No match: /properti/a/b/   ❌ (ada slash)

# 3. <slug:slug> — Slug (huruf, angka, dash, underscore)
path('properti/<slug:slug>/', ...)
# Match: /properti/beras-premium/  ✅
# Match: /properti/beras_01/      ✅

# 4. <uuid:id> — UUID format
path('order/<uuid:id>/', ...)
# Match: /order/075194d3-6885-417e-a8a8-6c931e272f00/  ✅

# 5. <path:rest> — Path (string TERMASUK /)
path('files/<path:rest>/', ...)
# Match: /files/folder/sub/file.txt/  ✅
```

---

## F3. Namespacing & Reverse URL — Deep Dive

### Kenapa Namespace Penting?

```python
# ═══ TANPA namespace — BENTROK! ═══
# apps/properti/urls.py
urlpatterns = [
    path('list/', PropertiListView.as_view(), name='list'),
]
# apps/sewa/urls.py
urlpatterns = [
    path('list/', KamarListView.as_view(), name='list'),  # NAMA SAMA!
]

# Di template:
# {% url 'list' %}  →  ??? Properti atau Sewa ???
# Django ambil yang TERAKHIR didaftarkan → BUG!

# ═══ DENGAN namespace — AMAN! ═══
# apps/properti/urls.py
app_name = 'properti'    # ← NAMESPACE
urlpatterns = [
    path('list/', PropertiListView.as_view(), name='list'),
]
# apps/sewa/urls.py
app_name = 'sewa'  # ← NAMESPACE BERBEDA
urlpatterns = [
    path('list/', KamarListView.as_view(), name='list'),
]

# Di template:
# {% url 'properti:list' %}     → /properti/list/     ✅
# {% url 'sewa:kamar' %}  → /sewa/kamar/   ✅
```

### reverse() vs reverse_lazy() — Kapan Pakai Yang Mana?

```python
from django.urls import reverse, reverse_lazy

# ═══ reverse() — evaluasi LANGSUNG ═══
# Pakai di DALAM method (function body)
def form_valid(self, form):
    form.save()
    url = reverse('properti:kategori_edit', kwargs={'pk': form.instance.pk})
    return redirect(url)
    # reverse() langsung evaluasi → '/properti/kategori/5/edit/'

# ═══ reverse_lazy() — evaluasi NANTI (lazy) ═══
# Pakai di class-level attribute
class KategoriCreateView(CreateView):
    success_url = reverse_lazy('properti:kategori')
    # KENAPA lazy?
    # Saat Python load class → URL belum siap (urls.py belum diproses)
    # reverse() langsung → ERROR: NoReverseMatch
    # reverse_lazy() → tunggu sampai URL dibutuhkan → AMAN!
```

**Aturan Sederhana:**
| Lokasi | Gunakan | Contoh |
|--------|---------|--------|
| Class attribute | `reverse_lazy()` | `success_url = reverse_lazy(...)` |
| Method body | `reverse()` | `url = reverse(...)` |
| Template | `{% url %}` | `{% url 'properti:list' %}` |
| redirect() | Nama langsung | `redirect('properti:list')` |

### Pattern redirect() yang Dipakai di Project:

```python
from django.shortcuts import redirect
from django.urls import reverse

# 1. Redirect via nama URL (PALING UMUM)
return redirect('properti:list')
# Django otomatis panggil reverse('properti:list')

# 2. Redirect dengan parameter
return redirect('properti:kategori_edit', pk=5)
# → /properti/kategori/5/edit/

# 3. Redirect via reverse() (lebih eksplisit)
url = reverse('properti:kategori_edit', kwargs={'pk': form.instance.pk})
return redirect(url)

# 4. Redirect via URL hardcode (TIDAK DISARANKAN)
return redirect('/properti/list/')
# ❌ Jika URL berubah → link mati
```

---

## F4. Error Handlers (404, 403, 500)

### Apa itu Error Handler?

Saat Django menemukan error, ia memanggil **handler function** yang menghasilkan halaman error custom.

### Setup di `config/urls.py`:

```python
# ═══ config/urls.py ═══
from config.views import (
    custom_error_404, custom_error_403,
    custom_error_400, custom_error_500
)

# Handler functions (di akhir file, SETELAH urlpatterns)
handler404 = custom_error_404   # Page Not Found
handler403 = custom_error_403   # Permission Denied
handler400 = custom_error_400   # Bad Request
handler500 = custom_error_500   # Server Error

# Test routes (untuk development)
urlpatterns = [
    path("test-error/404/", lambda r: custom_error_404(r, Exception("Test"))),
    path("test-error/403/", lambda r: custom_error_403(r, Exception("Test"))),
    # ...
]
```

### Kapan Handler Dipanggil?

| Handler | Kapan | Contoh |
|---------|-------|--------|
| `handler404` | URL tidak ditemukan | User akses `/halaman-tidak-ada/` |
| `handler403` | Permission ditolak | User tanpa akses klik menu admin |
| `handler400` | Request rusak | CSRF token expired, form corrupt |
| `handler500` | Server error | Bug di code Python → exception |

### PENTING: Error handler HANYA aktif saat `DEBUG = False`!
```python
# settings.py
DEBUG = True   # → Django tampilkan error traceback (development)
DEBUG = False  # → Django panggil handler404/403/500 (production)
```

---

## F5. Peta URL Lengkap Semua 14 Modul

### Daftar Semua Module URL:

```python
# config/urls.py — 14 modul terdaftar:
urlpatterns = [
    path("",           include("auth.urls")),                      # Auth
    path("",           include("apps.dashboard.urls")),            # Dashboard
    path("users/",     include("apps.user_management.urls")),      # Users
    path("properti/",    include("apps.properti.urls")),               # Properti
    path("sewa/", include("apps.sewa.urls")),            # Sewa
    path("penyewa/", include("apps.penyewa.urls")),            # Penyewa
    path("sewa/", include("apps.sewa.urls")),            # Sewa
    path("pos/",       include("apps.sewa.urls")),                  # POS
    path("biaya/",     include("apps.biaya.urls")),                # Biaya
    path("laporan/",   include("apps.laporan.urls")),              # Laporan
    path("activity-log/", include("apps.activity_log.urls")),      # Activity Log
    path("pengaturan/",include("apps.pengaturan.urls")),           # Pengaturan
    path("access/",    include("apps.permission_management.urls")),# Permission
    path("hr/",        include("apps.hr.urls")),                   # HR/SDM
    path("automation/",include("apps.automation.urls")),           # Automasi
]
```

### Pola CRUD Standar (Semua Modul Mengikuti Pola Ini):

```
/<modul>/                     → ListView (daftar)
/<modul>/add/                 → CreateView (tambah)
/<modul>/<int:pk>/            → DetailView (detail)
/<modul>/<int:pk>/edit/       → UpdateView (edit)
/<modul>/<int:pk>/delete/     → DeleteView (hapus)
```

### Contoh URL Map Lengkap — Modul Sewa:

| URL | View | Namespace Name | HTTP |
|-----|------|---------------|------|
| `/sewa/properti/` | PropertiListView | `sewa:properti` | GET |
| `/sewa/properti/add/` | PropertiCreateView | `sewa:properti_add` | GET/POST |
| `/sewa/properti/<pk>/edit/` | PropertiUpdateView | `sewa:properti_edit` | GET/POST |
| `/sewa/properti/<pk>/delete/` | PropertiDeleteView | `sewa:properti_delete` | POST |
| `/sewa/kamar/` | KamarListView | `sewa:kamar` | GET |
| `/sewa/transfer/` | TransferKamarView | `sewa:transfer` | GET |
| `/sewa/transfer/add/` | TransferKamarCreateView | `sewa:transfer_add` | GET/POST |
| `/sewa/transfer/<pk>/` | TransferKamarDetailView | `sewa:transfer_detail` | GET |
| `/sewa/transfer/<pk>/edit/` | TransferKamarUpdateView | `sewa:transfer_edit` | GET/POST |
| `/sewa/transfer/<pk>/approve/` | transfer_kamar_approve | `sewa:transfer_approve` | POST |
| `/sewa/transfer/<pk>/delete/` | TransferKamarDeleteView | `sewa:transfer_delete` | POST |
| `/sewa/adjustment/` | AdjustmentKamarView | `sewa:adjustment` | GET |
| `/sewa/adjustment/add/` | AdjustmentKamarCreateView | `sewa:adjustment_add` | GET/POST |
| `/sewa/api/kamar-tersedia/` | get_kamar_tersedia (FBV) | `sewa:api_kamar_tersedia` | GET |
| `/sewa/api/search-properti/` | search_properti (FBV) | `sewa:api_search_properti` | GET |

### Contoh URL Map — Modul HR (Terbanyak):

| URL | Namespace | Keterangan |
|-----|-----------|------------|
| `/hr/` | `hr:dashboard` | Dashboard HR |
| `/hr/departemen/` | `hr:departemen` | List Departemen |
| `/hr/departemen/add/` | `hr:departemen-add` | Tambah Departemen |
| `/hr/jabatan/` | `hr:jabatan` | List Jabatan |
| `/hr/karyawan/` | `hr:karyawan` | List Karyawan |
| `/hr/karyawan/<pk>/` | `hr:karyawan-detail` | Detail Karyawan |
| `/hr/absensi/` | `hr:absensi` | List Absensi |
| `/hr/absensi/clock-in/` | `hr:absensi-clock-in` | Clock In (FBV) |
| `/hr/absensi/clock-out/` | `hr:absensi-clock-out` | Clock Out (FBV) |
| `/hr/absensi/detect-face/` | `hr:detect-face` | Face Detection API |
| `/hr/penggajian/` | `hr:penggajian` | List Penggajian |
| `/hr/penggajian/generate/` | `hr:penggajian-generate` | Generate Gaji Bulanan |
| `/hr/pengaturan-absensi/` | `hr:pengaturan-absensi` | Pengaturan Absensi |

---

## I2. apps.py — AppConfig

### Apa itu apps.py?

Setiap app Django HARUS punya file `apps.py` yang berisi konfigurasi app.

```python
# ═══ apps/properti/apps.py ═══
from django.apps import AppConfig

class PropertiConfig(AppConfig):
    """Konfigurasi aplikasi Properti."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.properti'       # Path modul Python (WAJIB cocok dengan folder)
    verbose_name = 'Properti'    # Nama di admin panel
```

### Fungsi Setiap Attribute:

| Attribute | Fungsi | Contoh |
|-----------|--------|--------|
| `name` | Path Python ke app (WAJIB) | `'apps.properti'` |
| `verbose_name` | Nama tampilan di admin | `'Properti'` |
| `default_auto_field` | Tipe auto-increment PK | `'BigAutoField'` → `BIGINT` |
| `label` | Label unik app (opsional) | `'properti'` (default dari name) |

### Koneksi ke `settings.py`:

```python
# config/settings.py
INSTALLED_APPS = [
    # ...
    'apps.properti',           # Django cari PropertiConfig di apps/properti/apps.py
    'apps.sewa',        # Django cari SewaConfig di apps/sewa/apps.py
    'apps.penyewa',        # ...
    'apps.sewa',
    'apps.biaya',
    'apps.hr',
    # ...
]
```

### Method `ready()` — Kapan Digunakan?

```python
class SewaConfig(AppConfig):
    name = 'apps.sewa'

    def ready(self):
        """
        Dipanggil SEKALI saat Django startup.
        Gunakan untuk:
        - Import signals
        - Register signal handlers
        - Setup konfigurasi awal
        """
        import apps.sewa.signals  # Register signals
        # ↑ Signal akan dijalankan saat model save/delete
```

### Semua apps.py di Project SIMKOS:

| App | Config Class | verbose_name |
|-----|-------------|-------------- |
| `apps.properti` | PropertiConfig | Properti |
| `apps.sewa` | SewaConfig | Sewa |
| `apps.penyewa` | PenyewaConfig | Penyewa |
| `apps.sewa` | SewaConfig | Sewa |
| `apps.sewa` | PosConfig | Point of Sale |
| `apps.biaya` | BiayaConfig | Biaya |
| `apps.hr` | HrConfig | HR/SDM |
| `apps.laporan` | LaporanConfig | Laporan |
| `apps.dashboard` | DashboardConfig | Dashboard |
| `apps.pengaturan` | PengaturanConfig | Pengaturan |
| `apps.activity_log` | ActivityLogConfig | Activity Log |
| `apps.user_management` | UserManagementConfig | User Management |
| `apps.permission_management` | PermissionManagementConfig | Permission |
| `apps.automation` | AutomationConfig | Automasi |
| `apps.core` | CoreConfig | Core |

---

## I3. context_processors.py — Penyuntik Data Global

### Apa itu Context Processor?

Context Processor = **fungsi Python** yang **otomatis menyuntikkan data** ke SEMUA template.

```
Tanpa Context Processor:              Dengan Context Processor:
┌────────────────┐                   ┌────────────────────────┐
│ View 1         │                   │ context_processors.py  │
│   context = {  │                   │   return {             │
│     'setting'  │ ← harus manual    │     'NAMA_PERUSAHAAN'  │ ← OTOMATIS
│   }            │   di SETIAP view  │   }                    │   ke SEMUA
│ View 2         │                   │                        │   template
│   context = {  │                   │ Template mana saja:    │
│     'setting'  │                   │ {{ NAMA_PERUSAHAAN }}  │
│   }            │                   └────────────────────────┘
│ View 3 ...     │
│ (100 view!)    │
└────────────────┘
```

### Registrasi di `settings.py`:

```python
# config/settings.py
TEMPLATES = [{
    'OPTIONS': {
        'context_processors': [
            # ═══ BAWAAN DJANGO ═══
            'django.template.context_processors.debug',     # {{ debug }}
            'django.template.context_processors.request',   # {{ request }}
            'django.contrib.auth.context_processors.auth',  # {{ user }}, {{ perms }}
            'django.contrib.messages.context_processors.messages',  # {{ messages }}

            # ═══ CUSTOM PROJECT ═══
            'config.context_processors.my_setting',           # {{ MY_SETTING }}
            'config.context_processors.language_code',        # {{ LANG_CODE }}
            'config.context_processors.cookie_consent',       # {{ COOKIE_CONSENT }}
            'config.context_processors.environment',          # {{ ENVIRONMENT }}
            'config.context_processors.export_templates',     # {{ export_pdf_template }}
            'config.context_processors.pengaturan_perusahaan',# {{ COMPANY_NAME }}

            'apps.core.context_processors.permission_context',
            # ↑ {{ can_view }}, {{ can_create }}, {{ can_edit }}, {{ can_delete }}
            #   {{ accessible_subs }}
        ],
    },
}]
```

### Context Processor di `config/context_processors.py`:

#### 1. `my_setting` — Akses Settings dari Template
```python
def my_setting(request):
    """Expose settings object ke template."""
    return {'MY_SETTING': settings}
    # Template: {{ MY_SETTING.DEBUG }} → True/False
    # Template: {{ MY_SETTING.STATIC_URL }} → '/static/'
```

#### 2. `pengaturan_perusahaan` — Setting Perusahaan (Cached)
```python
def pengaturan_perusahaan(request):
    """
    Data perusahaan untuk header/footer template.
    CACHED 5 menit → menghindari query DB setiap request.
    """
    from django.core.cache import cache
    cache_key = 'ctx_pengaturan_perusahaan'
    cached = cache.get(cache_key)
    if cached:
        return cached

    from apps.pengaturan.models import PengaturanPerusahaan
    perusahaan = PengaturanPerusahaan.get_settings()

    result = {
        'COMPANY_NAME': perusahaan.nama_perusahaan,  # 'SIMKOS'
        'COMPANY_LOGO': perusahaan.logo,              # Logo URL
        'COMPANY_EMAIL': perusahaan.email,
        'COMPANY_PHONE': perusahaan.telepon,
        'COMPANY_ADDRESS': perusahaan.alamat,
    }
    cache.set(cache_key, result, 300)  # Cache 5 menit
    return result
    # Template: {{ COMPANY_NAME }} → 'SIMKOS'
```

#### 3. `export_templates` — Template Print (Cached)
```python
def export_templates(request):
    """
    Template header/footer untuk export PDF & Excel.
    CACHED 60 detik.
    """
    from django.core.cache import cache
    from apps.pengaturan.models import TemplateCetak

    cache_key = 'ctx_export_templates'
    cached = cache.get(cache_key)
    if cached:
        return cached

    result = {
        'export_pdf_template': TemplateCetak.get_template('export_pdf'),
        'export_excel_template': TemplateCetak.get_template('export_excel'),
    }
    cache.set(cache_key, result, 60)
    return result
    # Template: {{ export_pdf_template.header_nama_perusahaan }}
```

### Context Processor di `apps/core/context_processors.py`:

#### 4. `permission_context` — Cek Permission di Template
```python
def permission_context(request):
    """
    Menyuntikkan helper permission ke SEMUA template.
    Digunakan untuk hide/show menu dan tombol berdasarkan permission.
    """
    user = request.user
    if not user.is_authenticated:
        return {}

    return {
        'can_view': PermissionChecker(user, 'read'),
        'can_create': PermissionChecker(user, 'create'),
        'can_edit': PermissionChecker(user, 'write'),
        'can_delete': PermissionChecker(user, 'delete'),
        'accessible_subs': AccessibleSubsChecker(user),
    }
```

#### Cara Kerja `PermissionChecker` (Magic `__getattr__`):
```python
class PermissionChecker:
    def __init__(self, user, action):
        self.user = user
        self.action = action    # 'read', 'create', 'write', 'delete'

    def __getattr__(self, name):
        # Saat template akses: can_view.properti
        # name = 'properti'
        # Return PermissionChecker baru dengan module='properti'
        return PermissionChecker(self.user, self.action, name)

    def __bool__(self):
        # Saat template cek: {% if can_view.properti %}
        # Panggil has_permission(user, 'read', 'properti')
        return has_permission(self.user, self.action, self.module)
```

#### Pemakaian di Template:
```html
<!-- Sidebar: tampilkan menu hanya jika user punya akses -->
{% if can_view.properti %}
    <a href="{% url 'properti:list' %}">Daftar Properti</a>
{% endif %}

{% if can_create.properti %}
    <a href="{% url 'properti:tambah' %}" class="btn btn-primary">
        + Tambah Properti
    </a>
{% endif %}

<!-- Submodule check -->
{% if 'kategori' in accessible_subs.properti %}
    <a href="{% url 'properti:kategori' %}">Kategori</a>
{% endif %}
```

### Kenapa Caching Penting di Context Processor?

```
TANPA Cache:
Request 1  → Query DB → 5ms
Request 2  → Query DB → 5ms   ← Query SAMA setiap request!
Request 3  → Query DB → 5ms
...
1000 request/menit → 1000 query/menit → DB LAMBAT!

DENGAN Cache (5 menit):
Request 1   → Query DB → 5ms → Simpan ke cache
Request 2   → Baca cache → 0.1ms   ← 50x LEBIH CEPAT!
Request 3   → Baca cache → 0.1ms
...
1000 request/menit → 1 query/5 menit → DB SANTAI!
```

---

## I4. admin.py — Django Admin Panel

### Apa itu Django Admin?

Django Admin = **panel admin otomatis** untuk mengelola data database via browser. Akses di `/admin/`.

### Setup Dasar:

```python
# ═══ apps/properti/admin.py ═══
from django.contrib import admin
from apps.properti.models import Properti, Tipe Kamar, Kamar, Properti, Kamar

# Cara paling sederhana:
admin.site.register(Kategori)  # Register tanpa kustomisasi

# Cara dengan kustomisasi:
@admin.register(Properti)
class PropertiAdmin(admin.ModelAdmin):
    """
    Kustomisasi tampilan Properti di admin panel.
    """
    # ═══ KOLOM YANG DITAMPILKAN DI LIST ═══
    list_display = ['nama', 'sku', 'kategori', 'harga_beli', 'harga_jual', 'aktif']
    # ↑ Kolom yang muncul di halaman daftar
    # Output: tabel dengan kolom Nama, SKU, Kategori, Harga Beli, dll

    # ═══ FILTER SIDEBAR ═══
    list_filter = ['kategori', 'aktif', 'satuan']
    # ↑ Filter di sidebar kanan
    # User bisa filter: "Tampilkan hanya kategori Makanan"

    # ═══ KOLOM YANG BISA DICARI ═══
    search_fields = ['nama', 'sku', 'barcode']
    # ↑ Kotak pencarian di atas tabel
    # User ketik "Beras" → cari di nama, sku, barcode

    # ═══ KOLOM YANG BISA DIEDIT LANGSUNG ═══
    list_editable = ['aktif']
    # ↑ Checkbox "aktif" bisa diubah langsung dari list (tanpa membuka detail)

    # ═══ URUTAN DEFAULT ═══
    ordering = ['-id']
    # ↑ Urutkan dari terbaru (id terbesar)

    # ═══ JUMLAH ITEM PER HALAMAN ═══
    list_per_page = 25
```

### Contoh Nyata — Admin Kamar (Pencarian via ForeignKey):

```python
@admin.register(Kamar)
class KamarAdmin(admin.ModelAdmin):
    list_display = ['properti', 'properti', 'jumlah']
    list_filter = ['properti']

    # Pencarian via RELASI ForeignKey:
    search_fields = ['properti__nama', 'properti__nama']
    # ↑ properti__nama = akses field 'nama' di model Properti (via FK)
    # ↑ properti__nama = akses field 'nama' di model Properti (via FK)
    # User ketik "Beras" → Django query:
    #   SELECT * FROM kamar JOIN properti ON ... WHERE properti.nama LIKE '%Beras%'
```

### Inline Admin — Edit Child di Halaman Parent:

```python
# Tampilkan kamar langsung di halaman edit Properti
class KamarInline(admin.TabularInline):
    model = Kamar
    extra = 1  # 1 form kosong untuk tambah kamar baru

@admin.register(Properti)
class PropertiAdmin(admin.ModelAdmin):
    list_display = ['nama', 'sku', 'aktif']
    inlines = [KamarInline]
    # ↑ Saat edit Properti → di bawahnya ada tabel Kamar per Properti
```

### Semua Model yang Terdaftar di Admin:

| App | Model | Admin Class | Fitur |
|-----|-------|-------------|-------|
| properti | Kategori | KategoriAdmin | list_display, search |
| properti | Satuan | SatuanAdmin | list_display |
| properti | Properti | PropertiAdmin | list_display, filter, search |
| properti | Properti | PropertiAdmin | list_display |
| properti | Kamar | KamarAdmin | search via FK |

### Kapan Pakai Admin vs Custom View?

| Kebutuhan | Pakai Admin | Pakai Custom View |
|-----------|-------------|-------------------|
| Quick CRUD data master | ✅ | ❌ Overkill |
| UI khusus (dashboard, POS) | ❌ | ✅ |
| Permission granular | ❌ Terbatas | ✅ RBAC custom |
| User non-technical | ❌ Kurang friendly | ✅ UI custom |
| Development/debugging | ✅ Cepat | ❌ |

---

## I5. Kesalahan Umum & Best Practice

### ❌ Kesalahan Umum URL Routing

#### 1. Lupa `app_name` di urls.py
```python
# ❌ SALAH — NoReverseMatch saat pakai namespace
# apps/properti/urls.py
urlpatterns = [
    path('list/', PropertiListView.as_view(), name='list'),
]
# Template: {% url 'properti:list' %} → ERROR!

# ✅ BENAR
app_name = 'properti'  # ← WAJIB!
urlpatterns = [
    path('list/', PropertiListView.as_view(), name='list'),
]
```

#### 2. Urutan URL Salah (URL Bentrok)
```python
# ❌ SALAH — 'add' di-match sebagai <pk>!
urlpatterns = [
    path('<str:pk>/', DetailView.as_view()),  # 'add' cocok di sini!
    path('add/', CreateView.as_view()),       # Tidak pernah dipanggil!
]

# ✅ BENAR — spesifik dulu, umum belakangan
urlpatterns = [
    path('add/', CreateView.as_view()),       # Spesifik dulu
    path('<int:pk>/', DetailView.as_view()),  # <int:> lebih aman
]
```

#### 3. Pakai reverse() di Class Attribute
```python
# ❌ SALAH — ImproperlyConfigured saat startup!
class CreateView(CreateView):
    success_url = reverse('properti:list')  # URL belum siap!

# ✅ BENAR — lazy evaluation
class CreateView(CreateView):
    success_url = reverse_lazy('properti:list')  # Evaluasi nanti
```

#### 4. Lupa `.as_view()` untuk CBV
```python
# ❌ SALAH — TypeError!
path('list/', PropertiListView, name='list')

# ✅ BENAR
path('list/', PropertiListView.as_view(), name='list')
```

#### 5. Lupa `TemplateLayout.init()` di `get_context_data()`
```python
# ❌ SALAH — Sidebar hilang, layout rusak!
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    return context

# ✅ BENAR — WAJIB di semua view!
def get_context_data(self, **kwargs):
    context = TemplateLayout.init(self, super().get_context_data(**kwargs))
    return context
```

### ✅ Best Practice

| # | Practice | Contoh |
|---|----------|--------|
| 1 | Selalu pakai `app_name` | `app_name = 'properti'` |
| 2 | Gunakan `<int:pk>` bukan `<str:pk>` | Lebih aman, reject non-integer |
| 3 | Gunakan `reverse_lazy()` di attribute | `success_url = reverse_lazy(...)` |
| 4 | Mixin SEBELUM View di inheritance | `class X(Mixin, ListView)` |
| 5 | Trailing slash di URL | `'list/'` bukan `'list'` |
| 6 | Cache context processor yang query DB | `cache.set(key, result, 300)` |
| 7 | Register model di admin.py | Untuk quick debug data |
| 8 | Pakai namespace di semua `{% url %}` | `{% url 'properti:list' %}` |
| 9 | Satu `get_context_data` per view | Jangan override di 2 tempat |
| 10 | Dokumentasi URL di docstring apps | Seperti contoh sewa urls.py |

---

*Lanjut ke [05_TEMPLATE_DAN_LAYOUT.md](05_TEMPLATE_DAN_LAYOUT.md) →*
