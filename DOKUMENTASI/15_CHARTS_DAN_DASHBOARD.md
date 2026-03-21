# 📊 15 — Charts, Dashboard & Data Visualization — Panduan Lengkap

## DAFTAR ISI
- [A. Arsitektur Dashboard](#a-arsitektur-dashboard)
- [B. ApexCharts — Library Grafik](#b-apexcharts)
- [C. Area Chart (Tren Sewa)](#c-area-chart-tren-sewa)
- [D. Bar Chart (Perbandingan)](#d-bar-chart-perbandingan)
- [E. Radial Bar (Progress Lingkaran)](#e-radial-bar-progress-lingkaran)
- [F. Swiper Carousel (Slider)](#f-swiper-carousel-slider)
- [G. Dashboard View — Data dari 7 Modul](#g-dashboard-view)
- [H. Alur Data Lengkap: Database → Chart](#h-alur-data-lengkap)
- [I. Membuat Chart Baru](#i-membuat-chart-baru)
- [J. Responsive & Dark Mode Charts](#j-responsive--dark-mode)

---

## A. Arsitektur Dashboard

Dashboard SIMKOS kita menampilkan data dari **7 modul berbeda** dalam 1 halaman:

```
Dashboard = Data dari SELURUH bisnis di 1 layar:

┌─────────────────────────────────────────────────────────┐
│ HEADER: Filter Tanggal | Jam Real-time | Cabang | IP   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌── Row 1: Ringkasan Angka ─────────────────────────┐ │
│  │ [Total Aset] [Harga Beli] [Harga Jual] [Estimasi] │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌── Row 2: 2 Kolom ─────────────────────────────────┐ │
│  │ ┌─ col-md-8 ──────────┐ ┌─ col-md-4 ──────────┐  │ │
│  │ │ Area Chart:          │ │ Statistik:           │  │ │
│  │ │ Sewa Bulan Ini  │ │ Total Penyewa      │  │ │
│  │ │ [line + gradient]    │ │ Total Biaya           │  │ │
│  │ └─────────────────────┘ │ [Radial Bars]         │  │ │
│  │                          └──────────────────────┘  │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌── Row 3: 2 Kolom ─────────────────────────────────┐ │
│  │ ┌─ col-md-6 ──────────┐ ┌─ col-md-6 ──────────┐  │ │
│  │ │ Bar Chart:           │ │ Bar Chart:            │  │ │
│  │ │ Keuntungan / Cabang  │ │ Biaya per Kategori    │  │ │
│  │ └─────────────────────┘ └──────────────────────┘  │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌── Row 4: Swiper Carousels ────────────────────────┐ │
│  │ [Sewa Mingguan]    [Metode Pembayaran]        │ │
│  │ ← Slide 1 | 2 | 3 →    ← Slide 1 | 2 | 3 →      │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌── Row 5: Tabel + Timeline ────────────────────────┐ │
│  │ [Kamar Terpopuler]  [Pengguna Terbaru] [Aktivitas]  │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘

Sumber Data:
├── apps/sewa/models.py   → Tagihan Sewa, revenue, growth
├── apps/penyewa/models.py   → Kontrak Sewa, total beli
├── apps/properti/models.py      → Kamar, aset, kamar terpopuler
├── apps/biaya/models.py       → Biaya operasional
├── apps/sewa/models.py   → Properti, cabang
├── apps/hr/models.py          → Karyawan (opsional)
├── apps/sewa/models.py         → POS transaction
└── auth_user                  → Pengguna terbaru
```

### File-File yang Terlibat:

```
apps/dashboard/views.py        → DashboardView (1046 baris!)
                                  Mengumpulkan data dari 7 modul
                                  Query aggregate, annotate, filter

templates/dashboard/index.html  → Template (1313 baris!)
                                  HTML layout + CSS + JavaScript
                                  ApexCharts rendering
                                  Swiper carousel

static/vendor/libs/apex-charts/ → Library ApexCharts
static/vendor/libs/swiper/     → Library Swiper
static/vendor/css/pages/       → CSS cards dashboard
static/js/config.js            → Konfigurasi warna tema
```

---

## B. ApexCharts — Library Grafik

### Apa itu ApexCharts?

```
ApexCharts = Library JavaScript open-source untuk membuat grafik interaktif.
→ Support: Line, Area, Bar, Pie, Donut, Radial, Heatmap, dll
→ Responsive (otomatis resize)
→ Animasi smooth
→ Dark mode support
→ Website: https://apexcharts.com/

BUKAN Chart.js!
Di project ini kita pakai ApexCharts (bukan Chart.js).
```

### Cara Include di Template:

```html
{# Vendor CSS (di head) #}
{% block vendor_css %}
{{ block.super }}
<link rel="stylesheet" href="{% static 'vendor/libs/apex-charts/apex-charts.css' %}" />
{% endblock %}

{# Vendor JS (di bawah body) #}
{% block vendor_js %}
{{ block.super }}
<script src="{% static 'vendor/libs/apex-charts/apexcharts.js' %}"></script>
{% endblock %}
```

### Pola Dasar ApexCharts:

```javascript
// ═══ 3 LANGKAH membuat chart ═══

// 1. Siapkan elemen HTML di template:
//    <div id="myChart"></div>

// 2. Buat konfigurasi:
const config = {
    chart: {
        type: 'bar',          // Tipe chart
        height: 300,          // Tinggi pixel
    },
    series: [{
        name: 'Sewa',    // Label series
        data: [30, 40, 35, 50, 49, 60]  // Data angka
    }],
    xaxis: {
        categories: ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun']
    }
};

// 3. Render:
const chart = new ApexCharts(document.querySelector('#myChart'), config);
chart.render();
```

---

## C. Area Chart (Tren Sewa)

Area chart = garis + area berwarna di bawahnya. Cocok untuk **tren waktu**.

```javascript
// ═══ Seperti yang dipakai di dashboard ═══

const config = {
    chart: {
        type: 'area',           // Tipe: area chart
        height: 120,            // Tinggi compact
        sparkline: {
            enabled: true       // Mode sparkline: tanpa axis, minimal
        },
        toolbar: { show: false }  // Sembunyikan toolbar (zoom, export, dll)
    },
    
    series: [{
        name: 'Sewa',
        data: [150000, 200000, 180000, 250000, 220000]
        // ↑ Data dari Python (via json_script)
    }],
    
    // Garis:
    stroke: {
        width: 2,               // Ketebalan garis: 2px
        curve: 'smooth'         // Garis halus (bukan patah-patah)
    },
    
    // Isi area di bawah garis:
    fill: {
        type: 'gradient',       // Gradient dari atas (terang) ke bawah (transparan)
        gradient: {
            shadeIntensity: 0.4,
            opacityFrom: 0.8,   // Opacity atas: 80%
            opacityTo: 0.1,     // Opacity bawah: 10%
        }
    },
    
    // Warna:
    colors: ['#696CFF'],        // Warna primary Sneat (ungu)
    
    // Tooltip (popup saat hover):
    tooltip: {
        enabled: true,
        x: {
            formatter: function(val, opts) {
                return 'Tgl ' + labels[opts.dataPointIndex];
            }
        },
        y: {
            formatter: function(val) {
                return 'Rp ' + val.toLocaleString('id-ID');
                // 250000 → "Rp 250.000"
            }
        }
    },
    
    // Sumbu X:
    xaxis: {
        categories: ['1', '2', '3', '4', '5'],
        labels: { show: false }   // Sembunyikan label X (sparkline)
    },
    
    // Sumbu Y:
    yaxis: {
        min: 0,                   // Mulai dari 0
        labels: { show: false }   // Sembunyikan label Y
    }
};

const chartEl = document.querySelector('#saleThisMonthChart');
if (chartEl) {
    new ApexCharts(chartEl, config).render();
}
```

---

## D. Bar Chart (Perbandingan)

Bar chart = batang vertikal atau horizontal. Cocok untuk **membandingkan** kategori.

### Bar Chart Standar (Keuntungan per Cabang):

```javascript
const config = {
    chart: {
        type: 'bar',
        height: 153,
        toolbar: { show: false }
    },
    
    series: [{
        name: 'Profit',
        data: [50000, 80000, 60000, 90000, 70000]
    }],
    
    plotOptions: {
        bar: {
            borderRadius: 8,        // Ujung bar membulat
            columnWidth: '43%',     // Lebar bar 43% dari kolom
        }
    },
    
    colors: ['#71DD37'],            // Warna hijau (success)
    
    xaxis: {
        categories: ['Cab 1', 'Cab 2', 'Cab 3', 'Cab 4', 'Cab 5'],
        labels: {
            style: {
                colors: '#697a8d',  // Warna label teks
                fontSize: '11px',
            }
        }
    },
    
    yaxis: { labels: { show: false } },  // Sembunyikan sumbu Y
    dataLabels: { enabled: false },       // Jangan tampilkan angka di bar
    legend: { show: false },              // Sembunyikan legenda
};
```

### Bar Chart Distributed (Setiap Bar Beda Warna):

```javascript
const config = {
    chart: { type: 'bar', height: 314 },
    
    plotOptions: {
        bar: {
            distributed: true,     // ← KUNCI: setiap bar warna BERBEDA
            borderRadius: 8,
            columnWidth: '55%',
        }
    },
    
    series: [{
        name: 'Biaya',
        data: [30000, 50000, 20000, 45000, 15000]
    }],
    
    // Warna untuk SETIAP bar:
    colors: ['#E8E8FF', '#696CFF', '#E8E8FF', '#696CFF', '#E8E8FF'],
    // Bar 1: ungu muda, Bar 2: ungu tua, dst (bergantian)
    
    xaxis: {
        categories: ['Gaji', 'Sewa', 'Utilitas', 'Marketing', 'Lainnya'],
    }
};
```

---

## E. Radial Bar (Progress Lingkaran)

Radial bar = lingkaran progress. Cocok untuk **persentase**.

```javascript
const config = {
    chart: {
        type: 'radialBar',
        height: 90,
        width: 90,
        sparkline: { enabled: true }
    },
    
    series: [75],               // 75% progress
    
    plotOptions: {
        radialBar: {
            hollow: {
                size: '52%',    // Lubang tengah 52% dari diameter
                image: '/static/img/icons/order.png',  // Ikon di tengah
                imageWidth: 24,
                imageHeight: 24,
            },
            track: {
                background: '#E8E8FF',  // Warna track belakang
                strokeWidth: '100%'     // Lebar track
            },
            dataLabels: { show: false } // Sembunyikan angka persentase
        }
    },
    
    stroke: { lineCap: 'round' },  // Ujung progress membulat
    colors: ['#696CFF'],            // Warna progress
};
```

### Dynamic Radial Bars (Factory Function):

```javascript
// Di dashboard, kita pakai factory function untuk membuat radial bar yang dynamic:

function createRadialBar(color, value, icon) {
    return {
        chart: { type: 'radialBar', height: 90, width: 90, sparkline: { enabled: true } },
        series: [value],
        colors: [color],
        plotOptions: {
            radialBar: {
                hollow: { size: '52%', image: icon, imageWidth: 24, imageHeight: 24 },
                track: { background: '#E8E8FF' },
                dataLabels: { show: false }
            }
        }
    };
}

// Render semua radial bar dari HTML data attributes:
document.querySelectorAll('.chart-progress').forEach(el => {
    const config = createRadialBar(
        el.dataset.color,     // Dari: data-color="#696CFF"
        el.dataset.series,    // Dari: data-series="75"
        el.dataset.icon       // Dari: data-icon="/img/order.png"
    );
    new ApexCharts(el, config).render();
});
```

---

## F. Swiper Carousel (Slider)

Swiper = library slider/carousel responsif.

```html
{# ═══ HTML SLIDER ═══ #}
<div class="swiper" id="swiper-weekly-sales">
    <div class="swiper-wrapper">
        {# Setiap slide dibungkus swiper-slide: #}
        {% for item in weekly_sales %}
        <div class="swiper-slide">
            <div class="card bg-primary text-white p-3">
                <h6>{{ item.kategori }}</h6>
                <h3>{{ item.total|rupiah }}</h3>
                <span>{{ item.qty }} item terjual</span>
            </div>
        </div>
        {% endfor %}
    </div>
    <div class="swiper-pagination"></div>
</div>
```

```javascript
// ═══ INISIALISASI SWIPER ═══
new Swiper('#swiper-weekly-sales', {
    loop: true,               // Putar terus (slide terakhir → pertama)
    autoplay: {
        delay: 2500,           // Geser otomatis per 2.5 detik
        disableOnInteraction: false,  // Tetap autoplay setelah user interact
    },
    pagination: {
        el: '.swiper-pagination',
        clickable: true,       // Dot pagination bisa diklik
    },
    slidesPerView: 1,          // 1 slide terlihat
    spaceBetween: 16,          // Jarak antar slide: 16px
    breakpoints: {
        768: { slidesPerView: 2 },  // Tablet: 2 slide
        1200: { slidesPerView: 3 }, // Desktop: 3 slide
    }
});
```

---

## G. Dashboard View — Data dari 7 Modul

### Ringkasan `DashboardView` (1046 baris):

```python
# apps/dashboard/views.py

class DashboardView(TemplateView):
    """
    View TERBESAR di project: 1046 baris!
    Mengumpulkan data dari SELURUH modul.
    """
    
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        
        # ─── DATA PROPERTI ───
        # Query: Hitung total aset = SUM(harga_beli × kamar)
        properti_qs = Properti.objects.aggregate(
            total_aset=Sum(F('harga_beli') * F('kamar')),
            total_harga_beli=Sum('harga_beli'),
            total_harga_jual=Sum('harga_jual'),
        )
        context['total_aset'] = properti_data['total_aset'] or 0
        
        # ─── DATA PENJUALAN ───
        # Filter: bulan ini
        bulan_ini = SalesOrder.objects.filter(
            tanggal__year=today.year,
            tanggal__month=today.month,
        )
        context['total_sewa'] = bulan_ini.aggregate(Sum('harga_sewa'))
        
        # Chart data: sewa per hari
        sales_per_day = bulan_ini.values('tanggal__day').annotate(
            total=Sum('harga_sewa')
        ).order_by('tanggal__day')
        context['sales_chart_data'] = [float(s['total']) for s in sales_per_day]
        context['sales_chart_labels'] = [str(s['tanggal__day']) for s in sales_per_day]
        
        # ─── DATA KEUNTUNGAN PER CABANG ───
        cabang = Properti.objects.all()
        profit_data = []
        for g in cabang:
            revenue = SalesOrder.objects.filter(properti=g).aggregate(Sum('harga_sewa'))
            cost = KontrakSewa.objects.filter(properti=g).aggregate(Sum('harga_sewa'))
            profit = (revenue['grand_total__sum'] or 0) - (cost['grand_total__sum'] or 0)
            profit_data.append(float(profit))
        context['live_visitors_data'] = profit_data
        context['cabang_names'] = [g.nama for g in cabang]
        
        # ─── DATA BIAYA PER KATEGORI ───
        biaya_qs = Biaya.objects.values('tipe_kamar__nama').annotate(total=Sum('jumlah'))
        context['visits_by_day_data'] = [float(b['total']) for b in biaya_qs]
        context['biaya_labels'] = [b['tipe_kamar__nama'][:6] for b in biaya_qs]
        
        # ─── KAMAR TERPOPULER ─── (top 10)
        context['kamar_terpopuler'] = TagihanSewaItem.objects.values(
            'properti__nama'
        ).annotate(
            total_qty=Sum('quantity')
        ).order_by('-total_qty')[:10]
        
        # ─── PENGGUNA TERBARU ───
        context['recent_users'] = User.objects.order_by('-date_joined')[:5]
        
        return context
```

---

## H. Alur Data Lengkap: Database → Chart

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   DATABASE   │     │    PYTHON    │     │  JAVASCRIPT  │
│   (SQLite)   │ ──→ │  (View.py)   │ ──→ │ (ApexCharts) │
└──────────────┘     └──────────────┘     └──────────────┘

Langkah 1: DATABASE → PYTHON
─────────────────────────────
# Django ORM query
sales = SalesOrder.objects.filter(
    tanggal__month=2
).values('tanggal__day').annotate(
    total=Sum('harga_sewa')
)

# SQL yang dijalankan:
# SELECT tanggal AS day, SUM(grand_total) AS total
# FROM sewa_salesorder
# WHERE MONTH(tanggal) = 2
# GROUP BY tanggal

# Hasil: [{'tanggal__day': 1, 'total': 150000}, ...]

Langkah 2: PYTHON → CONTEXT
─────────────────────────────
chart_data = [float(s['total']) for s in sales]  
# [150000.0, 200000.0, 180000.0]

chart_labels = [str(s['tanggal__day']) for s in sales]  
# ['1', '2', '3']

context['sales_chart_data'] = chart_data
context['sales_chart_labels'] = chart_labels

Langkah 3: CONTEXT → HTML (json_script)
────────────────────────────────────────
{{ sales_chart_data|json_script:"sales-data" }}
# Output: <script id="sales-data">[150000.0, 200000.0, 180000.0]</script>

Langkah 4: HTML → JAVASCRIPT (JSON.parse)
──────────────────────────────────────────
const data = JSON.parse(document.getElementById('sales-data').textContent);
// data = [150000, 200000, 180000]

Langkah 5: JAVASCRIPT → CHART (ApexCharts)
────────────────────────────────────────────
new ApexCharts(element, {
    series: [{ data: data }],
    // ...
}).render();
// → CHART MUNCUL DI LAYAR! 🎉
```

---

## I. Membuat Chart Baru

### Langkah Step-by-Step:

```python
# ═══ LANGKAH 1: Tambah data di views.py ═══

def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    
    # Contoh: chart kamar per tipe
    kamar_per_tipe_data = Properti.objects.values('tipe_kamar__nama').annotate(
        jumlah=Count('id')
    ).order_by('-jumlah')
    
    context['kamar_per_tipe'] = [p['jumlah'] for p in kamar_per_tipe_data]
    context['tipe_names'] = [p['tipe_kamar__nama'] for p in kamar_per_tipe_data]
    return context
```

```html
{# ═══ LANGKAH 2: Inject data ke template ═══ #}
{{ kamar_per_tipe|json_script:"kamar-tipe-data" }}
{{ tipe_names|json_script:"kamar-tipe-labels" }}

{# ═══ LANGKAH 3: Buat elemen HTML ═══ #}
<div class="card">
    <div class="card-header"><h5>Kamar per Tipe</h5></div>
    <div class="card-body">
        <div id="kamarPerTipeChart"></div>
    </div>
</div>
```

```javascript
// ═══ LANGKAH 4: Render chart ═══
const data = JSON.parse(document.getElementById('kamar-tipe-data').textContent);
const labels = JSON.parse(document.getElementById('kamar-tipe-labels').textContent);

const chartEl = document.querySelector('#kamarPerTipeChart');
if (chartEl) {
    new ApexCharts(chartEl, {
        chart: { type: 'bar', height: 300, toolbar: { show: false } },
        series: [{ name: 'Kamar', data: data }],
        plotOptions: { bar: { borderRadius: 6, columnWidth: '50%' } },
        colors: ['#696CFF'],
        xaxis: { categories: labels },
        dataLabels: { enabled: false },
    }).render();
}
```

---

## J. Responsive & Dark Mode Charts

### Responsive (Otomatis Resize):

```javascript
{
    chart: { type: 'bar', height: 300 },
    
    responsive: [
        {
            breakpoint: 992,     // Di bawah 992px (tablet):
            options: {
                chart: { height: 250 },
                plotOptions: { bar: { columnWidth: '55%' } }
            }
        },
        {
            breakpoint: 576,     // Di bawah 576px (HP):
            options: {
                chart: { height: 200 },
                plotOptions: { bar: { columnWidth: '70%' } }
            }
        }
    ]
}
```

### Dark Mode (Otomatis Ikut Tema):

```javascript
// Sneat menyediakan variabel global isDarkStyle:
let labelColor, borderColor;

if (isDarkStyle) {
    // Config dari static/js/config.js:
    labelColor = config.colors_dark.textMuted;    // '#7C7C9A'
    borderColor = config.colors_dark.borderColor;  // '#444564'
} else {
    labelColor = config.colors.textMuted;          // '#a8aab4'
    borderColor = config.colors.borderColor;       // '#e6e5e8'
}

// Pakai di chart config:
{
    xaxis: {
        labels: { style: { colors: labelColor } }
    },
    grid: {
        borderColor: borderColor
    }
}
```

---

*Selesai! Semua 16 file dokumentasi mencakup pembuatan SIMKOS dari A-Z.*
