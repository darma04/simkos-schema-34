# 🔌 13 — API & AJAX di Project SIMKOS — Panduan Lengkap

## DAFTAR ISI
- [A. Apa itu API?](#a-apa-itu-api)
- [B. Apakah SIMKOS Kita Punya API?](#b-apakah-simkos-kita-punya-api)
- [C. Pola AJAX di Project SIMKOS](#c-pola-ajax-di-project-simkos)
- [D. CSRF Token — Keamanan Form & AJAX](#d-csrf-token)
- [E. Contoh Lengkap: AJAX Delete](#e-contoh-lengkap-ajax-delete)
- [F. Contoh Lengkap: AJAX Search (Select2)](#f-contoh-lengkap-ajax-search)
- [G. json_script — Bridge Data Python → JavaScript](#g-json_script)
- [H. Membuat Endpoint AJAX Baru](#h-membuat-endpoint-ajax-baru)

---

## A. Apa itu API?

### Definisi:

```
API = Application Programming Interface
    = Cara 2 program BERKOMUNIKASI satu sama lain

Analogi:
┌────────────────────────────────────────────────────────┐
│ API ≈ PELAYAN RESTORAN                                │
│                                                        │
│ Kamu (Frontend)      → Pesan makanan (request)        │
│ Pelayan (API)        → Antar pesanan ke dapur         │
│ Dapur (Backend/DB)   → Masak makanan (proses data)    │
│ Pelayan (API)        → Antar makanan kembali (response)│
│ Kamu                 → Makan (tampilkan data)         │
│                                                        │
│ Kamu TIDAK PERNAH masuk ke dapur langsung!            │
│ Selalu melalui pelayan (API).                         │
└────────────────────────────────────────────────────────┘
```

### Jenis API:

```
1. REST API (RESTful)
   → Endpoint URL yang return DATA (JSON/XML)
   → Contoh: GET /api/properti/ → return JSON list properti
   → Framework populer: Django REST Framework (DRF)
   → Biasa dipakai untuk: Mobile app, SPA (React/Vue), integrasi

2. Internal AJAX Endpoint
   → URL yang return JSON, tapi BUKAN REST API formal
   → Tidak ada autentikasi token (pakai session cookie)
   → Tidak ada versioning (/api/v1/...)
   → Dipakai oleh JavaScript di halaman yang SAMA
   → ← INI yang dipakai di project SIMKOS kita!

3. GraphQL API
   → Query language untuk API (tidak digunakan di project ini)
```

---

## B. Apakah SIMKOS Kita Punya API?

### Jawaban: TIDAK punya REST API formal, TAPI punya AJAX endpoints.

```
Project SIMKOS ini = Server-Side Rendered (SSR):
→ Django render HTML di server → kirim ke browser
→ BUKAN Single Page Application (SPA)
→ BUKAN Mobile App yang butuh REST API

TAPI ada "mini API" dalam bentuk AJAX endpoints:
→ URL yang return JsonResponse (bukan HTML)
→ Dipanggil oleh JavaScript di browser
→ Contoh: hapus data, search properti, update status
```

### Semua AJAX Endpoints di Project:

| URL | Method | Fungsi | File |
|-----|--------|--------|------|
| `/properti/<id>/delete/` | DELETE | Hapus properti | `apps/properti/views.py` |
| `/properti/kategori/<id>/delete/` | DELETE | Hapus kategori | `apps/properti/views.py` |
| `/sewa/so/<id>/delete/` | DELETE | Hapus Tagihan Sewa | `apps/sewa/views.py` |
| `/penyewa/po/<id>/delete/` | DELETE | Hapus Kontrak Sewa | `apps/penyewa/views.py` |
| `/sewa/transfer/<id>/delete/` | DELETE | Hapus transfer kamar | `apps/sewa/views.py` |
| `/sewa/properti/<id>/delete/` | DELETE | Hapus properti | `apps/sewa/views.py` |
| `/hr/karyawan/<id>/delete/` | DELETE | Hapus karyawan | `apps/hr/views.py` |
| `/biaya/<id>/delete/` | DELETE | Hapus biaya | `apps/biaya/views.py` |
| `/access/roles/<id>/delete/` | POST | Hapus role | `apps/permission_management/views_roles.py` |
| `/pos/complete/` | POST | Selesaikan POS | `apps/sewa/views.py` |
| `/properti/search/` | GET | Search properti (Select2 AJAX) | `apps/properti/views.py` |

---

## C. Pola AJAX di Project SIMKOS

### Apa itu AJAX?

```
AJAX = Asynchronous JavaScript And XML
     = Teknik kirim/terima data TANPA reload halaman

Tanpa AJAX:
1. User klik hapus → Browser reload → Server proses → Kirim HTML baru → Render ulang
   (Layar putih sebentar — UX buruk)

Dengan AJAX:
1. User klik hapus → JavaScript kirim request di background
2. Server proses → Kirim response JSON (kecil)
3. JavaScript update halaman TANPA reload
   (Halaman tidak berkedip — UX bagus)
```

### Pola Standar AJAX di Project:

```
┌──────────── FRONTEND ─────────────┐    ┌──────── BACKEND ────────┐
│                                    │    │                          │
│ 1. User klik "Hapus"              │    │                          │
│    ↓                               │    │                          │
│ 2. confirmDelete(id, nama)        │    │                          │
│    → Tampilkan modal konfirmasi   │    │                          │
│    ↓                               │    │                          │
│ 3. User klik "Ya, Hapus"         │    │                          │
│    ↓                               │    │                          │
│ 4. fetch('/properti/5/delete/', {   │──→ │ 5. DeleteView.delete()  │
│        method: 'DELETE',           │    │    → properti.delete()     │
│        headers: {                  │    │    → return JsonResponse │
│          'X-CSRFToken': token      │    │      {success: true}     │
│        }                           │    │                          │
│    })                              │    │                          │
│    ↓                               │ ←──│                          │
│ 6. .then(response => {            │    │                          │
│       if (data.success)            │    │                          │
│         location.reload()          │    │                          │
│       else                         │    │                          │
│         alert(data.message)        │    │                          │
│    })                              │    │                          │
└────────────────────────────────────┘    └──────────────────────────┘
```

---

## D. CSRF Token — Keamanan Form & AJAX

### Apa itu CSRF?

```
CSRF = Cross-Site Request Forgery
     = Serangan di mana website LAIN mengirimkan request
       ke server KITA atas nama user yang sedang login.

Contoh serangan:
1. User login ke SIMKOS kita (session aktif)
2. User buka website jahat di tab lain
3. Website jahat punya form tersembunyi:
   <form action="https://erp-kita.com/properti/5/delete/" method="POST">
   <script>document.forms[0].submit()</script>
4. Browser kirim request KE SERVER KITA dengan cookie user!
5. Server kira ini request sah → data TERHAPUS!

CSRF Token mencegah ini:
→ Setiap form punya token RAHASIA yang hanya diketahui server
→ Website lain TIDAK tahu token ini → request ditolak
```

### Cara Pakai di Form HTML:

```html
<form method="POST">
    {% csrf_token %}
    {# Output: <input type="hidden" name="csrfmiddlewaretoken" value="abc123..."> #}
    ... field-field form ...
</form>
```

### Cara Pakai di AJAX:

```javascript
// Cara 1: Ambil dari hidden input (jika ada {% csrf_token %} di halaman)
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// Cara 2: Ambil dari cookie
function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1);
        }
    }
    return '';
}

// Kirim di header request:
fetch('/properti/5/delete/', {
    method: 'DELETE',
    headers: {
        'X-CSRFToken': csrfToken,      // ← Header wajib untuk POST/PUT/DELETE
        'Content-Type': 'application/json',
    }
});
```

---

## E. Contoh Lengkap: AJAX Delete

### Backend (Python):

```python
# apps/properti/views.py

class PropertiDeleteView(SubModulePermissionMixin, DeleteView):
    model = Properti
    permission_module = 'properti'
    permission_sub_module = 'daftar_properti'
    permission_action = 'delete'
    
    def delete(self, request, *args, **kwargs):
        try:
            properti = self.get_object()       # Ambil properti berdasarkan pk di URL
            nama = properti.nama
            
            # Cek apakah properti memiliki relasi yang menghalangi delete
            if properti.kontraksewa_set.exists():
                return JsonResponse({
                    'success': False,
                    'message': f'Tidak bisa menghapus "{nama}" — masih ada di Tagihan Sewa'
                }, status=400)
            
            properti.delete()
            return JsonResponse({
                'success': True,
                'message': f'Properti "{nama}" berhasil dihapus!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Gagal: {str(e)}'
            }, status=500)
```

### Frontend (JavaScript):

```javascript
// ═══ DI TEMPLATE HTML ═══

// Tombol hapus di setiap row tabel:
// <button onclick="confirmDelete({{ properti.pk }}, '{{ properti.nama }}')">Hapus</button>

let deleteId = null;

function confirmDelete(id, nama) {
    deleteId = id;
    document.getElementById('deleteName').textContent = nama;
    // Buka modal konfirmasi Bootstrap
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    modal.show();
}

// Event listener tombol "Ya, Hapus" di modal
document.getElementById('confirmDeleteBtn').addEventListener('click', function() {
    if (!deleteId) return;
    
    const btn = this;
    // Disable tombol + tampilkan spinner (mencegah double-click)
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Menghapus...';
    
    // Kirim AJAX DELETE request
    fetch(`/properti/${deleteId}/delete/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Berhasil → reload halaman
            location.reload();
        } else {
            // Gagal → tampilkan error
            alert(data.message);
            btn.disabled = false;
            btn.innerHTML = '<i class="ri-delete-bin-line me-1"></i>Ya, Hapus';
        }
    })
    .catch(error => {
        alert('Terjadi kesalahan jaringan');
        btn.disabled = false;
    });
});
```

---

## F. Contoh Lengkap: AJAX Search (Select2)

### Backend — Search Endpoint:

```python
# apps/properti/views.py

class PropertiSearchView(SubModulePermissionMixin, ListView):
    """
    AJAX endpoint untuk search properti (dipakai oleh Select2 dropdown).
    
    URL: /properti/search/?q=keyword
    Response: JSON list properti yang cocok
    """
    permission_module = 'properti'
    permission_action = 'read'
    
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        
        properti_qs = Properti.objects.filter(
            nama__icontains=query      # Case-insensitive LIKE '%query%'
        )[:20]                         # Limit 20 hasil
        
        # Format untuk Select2:
        results = [
            {
                'id': p.pk,
                'text': p.nama,
                'sku': p.sku,
                'harga': float(p.harga_jual),
                'kamar': p.kamar,
            }
            for p in properti_qs
        ]
        
        return JsonResponse({
            'results': results,
            'pagination': {'more': False}
        })
```

### Frontend — Select2 AJAX:

```javascript
// Inisialisasi Select2 dengan AJAX search
$('#properti-dropdown').select2({
    placeholder: 'Cari properti...',
    minimumInputLength: 2,          // Mulai search setelah 2 karakter
    
    ajax: {
        url: '/properti/search/',     // URL endpoint backend
        dataType: 'json',
        delay: 300,                 // Tunggu 300ms sebelum request (debounce)
        
        data: function(params) {
            return { q: params.term };  // Kirim keyword sebagai ?q=keyword
        },
        
        processResults: function(data) {
            return { results: data.results };
        }
    },
    
    // Custom format tampilan hasil search:
    templateResult: function(item) {
        if (!item.id) return item.text;
        return $(`
            <div class="d-flex justify-content-between">
                <span><strong>${item.text}</strong> (${item.sku})</span>
                <span class="text-muted">Kamar: ${item.kamar}</span>
            </div>
        `);
    }
});
```

---

## G. json_script — Bridge Data Python → JavaScript

### Kenapa Pakai json_script?

```
Masalah: Bagaimana mengirim data dari Python ke JavaScript?

Cara LAMA (rentan XSS):
  <script>
  var data = "{{ data_python }}";
  // Jika data mengandung </script> → RUSAK!
  // Jika data mengandung ' atau " → RUSAK!
  </script>

Cara AMAN (json_script):
  {{ data|json_script:"my-data" }}
  → Django auto-escape semua karakter berbahaya
  → Aman dari XSS attack
```

### Cara Pakai:

```python
# views.py — kirim data
context['chart_data'] = [100, 200, 300, 400]
context['chart_labels'] = ['Jan', 'Feb', 'Mar', 'Apr']
context['user_info'] = {'nama': 'Admin', 'role': 'Super Admin'}
```

```html
{# template.html — bridge ke JavaScript #}

{# Langkah 1: Inject data sebagai JSON di HTML #}
{{ chart_data|json_script:"chart-data" }}
{{ chart_labels|json_script:"chart-labels" }}
{{ user_info|json_script:"user-info" }}

{# Output HTML (aman!): #}
{# <script id="chart-data" type="application/json">[100, 200, 300, 400]</script> #}
{# <script id="chart-labels" type="application/json">["Jan", "Feb", "Mar", "Apr"]</script> #}
{# <script id="user-info" type="application/json">{"nama": "Admin", "role": "Super Admin"}</script> #}

{# Langkah 2: Baca dari JavaScript #}
<script>
const chartData = JSON.parse(document.getElementById('chart-data').textContent);
// chartData = [100, 200, 300, 400]

const chartLabels = JSON.parse(document.getElementById('chart-labels').textContent);
// chartLabels = ['Jan', 'Feb', 'Mar', 'Apr']

const userInfo = JSON.parse(document.getElementById('user-info').textContent);
// userInfo = {nama: 'Admin', role: 'Super Admin'}
</script>
```

---

## H. Membuat Endpoint AJAX Baru

### Langkah-Langkah:

```python
# ═══ LANGKAH 1: Buat view yang return JsonResponse ═══
# apps/properti/views.py

from django.http import JsonResponse

class PropertiToggleAktifView(SubModulePermissionMixin, UpdateView):
    """Toggle status aktif/nonaktif properti via AJAX."""
    model = Properti
    permission_module = 'properti'
    permission_action = 'write'
    
    def post(self, request, *args, **kwargs):
        properti = self.get_object()
        properti.aktif = not properti.aktif   # Toggle boolean
        properti.save()
        return JsonResponse({
            'success': True,
            'aktif': properti.aktif,
            'message': f'{properti.nama} {"diaktifkan" if properti.aktif else "dinonaktifkan"}'
        })


# ═══ LANGKAH 2: Tambah URL ═══
# apps/properti/urls.py

path('<int:pk>/toggle-aktif/', views.PropertiToggleAktifView.as_view(), name='toggle_aktif'),


# ═══ LANGKAH 3: Panggil dari JavaScript ═══
```

```javascript
// Di template:
function toggleAktif(id) {
    fetch(`/properti/${id}/toggle-aktif/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        }
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            // Update badge di tabel tanpa reload
            const badge = document.querySelector(`#status-${id}`);
            if (data.aktif) {
                badge.className = 'badge bg-label-success';
                badge.textContent = 'Aktif';
            } else {
                badge.className = 'badge bg-label-danger';
                badge.textContent = 'Nonaktif';
            }
        }
    });
}
```

---

*Lanjut ke [14_TEMPLATE_TAGS_DAN_FILTERS.md](14_TEMPLATE_TAGS_DAN_FILTERS.md) →*
