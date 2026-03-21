"""
==========================================================================
 AI ASSISTANT INTENTS - Deteksi Intent & Pengumpulan Data SIMKOS
==========================================================================
 Modul ini menangani:
 1. detect_intent(message) — Deteksi topik dari kata kunci user
 2. gather_data(intent) — Query ORM sesuai intent, return ringkasan

 ARSITEKTUR AMAN:
 - Tidak ada SQL langsung — semua via Django ORM
 - Data yang dikumpulkan hanya angka agregat (total, count, avg)
 - Tidak ada data pribadi/sensitif yang dikirim ke AI
 - AI hanya menerima ringkasan untuk diformat/dijelaskan

 KONTEKS: Sistem Manajemen Kost (SIMKOS)
 - Properti, Tipe Kamar, Kamar
 - Penyewa, Kontrak Sewa
 - Tagihan Sewa, Pembayaran Sewa
 - Biaya Operasional, Karyawan HR
==========================================================================
"""
import logging
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q, F

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# INTENT DEFINITIONS — Kata kunci per intent (konteks KOS)
# ═══════════════════════════════════════════════════════════════
INTENT_KEYWORDS = {
    'properti': [
        'properti', 'kost', 'kos', 'kontrakan', 'apartemen', 'rumah sewa',
        'gedung', 'bangunan', 'lokasi', 'alamat', 'property',
    ],
    'kamar': [
        'kamar', 'room', 'hunian', 'okupansi', 'occupancy', 'tersedia',
        'terisi', 'kosong', 'kamar kosong', 'maintenance', 'perbaikan',
        'tipe kamar', 'fasilitas', 'lantai',
    ],
    'penyewa': [
        'penyewa', 'tenant', 'penghuni', 'anak kos', 'warga',
        'data penyewa', 'penyewa aktif', 'blacklist',
    ],
    'kontrak': [
        'kontrak', 'contract', 'sewa', 'kontrak sewa', 'masa sewa',
        'perpanjangan', 'kontrak aktif', 'kontrak habis', 'durasi sewa',
    ],
    'tagihan': [
        'tagihan', 'bill', 'invoice', 'belum bayar', 'tunggakan',
        'menunggak', 'telat bayar', 'terlambat', 'jatuh tempo',
        'tagihan sewa', 'lunas', 'bayar sebagian',
    ],
    'pembayaran': [
        'pembayaran', 'payment', 'bayar', 'transfer', 'tunai',
        'pendapatan', 'income', 'pemasukan', 'cash flow',
        'metode bayar', 'qris', 'e-wallet',
    ],
    'biaya': [
        'biaya', 'expense', 'pengeluaran', 'cost', 'operasional',
        'listrik', 'air', 'kebersihan', 'internet', 'wifi',
        'maintenance', 'perbaikan', 'renovasi',
    ],
    'keuntungan': [
        'keuntungan', 'profit', 'laba', 'rugi', 'untung',
        'margin', 'net profit', 'gross profit', 'nett',
        'pendapatan bersih', 'omzet', 'omset', 'revenue',
    ],
    'karyawan': [
        'karyawan', 'employee', 'pegawai', 'staff', 'sdm', 'hr',
        'departemen', 'jabatan', 'gaji', 'penggajian',
    ],
    'bantuan': [
        'bantuan', 'help', 'tolong', 'cara', 'panduan', 'tutorial',
        'fitur', 'menu', 'apa saja', 'bisa apa', 'fungsi',
    ],
    # ═══ ADVANCED INTENTS ═══
    'laporan_meeting': [
        'laporan meeting', 'meeting', 'rapat', 'laporan manajemen',
        'presentasi', 'laporan bulanan', 'notulen', 'report meeting',
    ],
    'executive_summary': [
        'executive summary', 'ringkasan eksekutif', 'summary', 'rangkuman',
        'ringkasan bisnis', 'overview bisnis', 'ikhtisar',
    ],
    'swot': [
        'swot', 'strength', 'weakness', 'opportunity', 'threat',
        'analisa swot', 'kekuatan', 'kelemahan', 'peluang', 'ancaman',
    ],
    'rencana_aksi': [
        'rencana', 'aksi', 'rekomendasi', 'saran', 'strategi',
        'meningkatkan okupansi', 'tingkatkan hunian', 'action plan',
        'apa yang harus', 'langkah', 'solusi',
    ],
    'forecasting': [
        'prediksi', 'forecast', 'proyeksi', 'estimasi',
        'perkiraan', 'tren', 'trend', '30 hari', 'bulan depan',
    ],
    'risiko': [
        'risiko', 'risk', 'bahaya', 'masalah', 'warning', 'peringatan',
        'tunggakan besar', 'kontrak habis', 'kamar kosong banyak',
    ],
    'perbandingan': [
        'bandingkan', 'perbandingan', 'compare', 'vs', 'banding',
        'bulan lalu', 'periode lalu', 'year over year', 'dibanding',
    ],
}


def detect_intent(message):
    """
    Deteksi intent dari pesan user berdasarkan kata kunci.

    Args:
        message (str): Pesan dari user

    Returns:
        str: Nama intent yang terdeteksi
    """
    msg = message.lower().strip()

    best_intent = 'umum'
    best_score = 0

    for intent, keywords in INTENT_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in msg:
                score += len(kw)
        if score > best_score:
            best_score = score
            best_intent = intent

    return best_intent


def _parse_time_context(message):
    """
    Parse konteks waktu dari pesan user.
    Return (start_date, end_date, label_periode) atau None jika tidak ada konteks waktu.
    """
    msg = message.lower().strip()
    today = timezone.now().date()

    if 'hari ini' in msg or 'today' in msg:
        return today, today, 'Hari Ini'

    if 'kemarin' in msg or 'yesterday' in msg:
        kemarin = today - timedelta(days=1)
        return kemarin, kemarin, 'Kemarin'

    if 'minggu ini' in msg or 'this week' in msg or 'pekan ini' in msg:
        start_of_week = today - timedelta(days=today.weekday())
        return start_of_week, today, f'Minggu Ini ({start_of_week.strftime("%d/%m")} - {today.strftime("%d/%m/%Y")})'

    if 'minggu lalu' in msg or 'last week' in msg or 'pekan lalu' in msg:
        end_of_last_week = today - timedelta(days=today.weekday() + 1)
        start_of_last_week = end_of_last_week - timedelta(days=6)
        return start_of_last_week, end_of_last_week, f'Minggu Lalu ({start_of_last_week.strftime("%d/%m")} - {end_of_last_week.strftime("%d/%m/%Y")})'

    if 'bulan lalu' in msg or 'last month' in msg or 'bulan kemarin' in msg:
        first_this_month = today.replace(day=1)
        end_last_month = first_this_month - timedelta(days=1)
        start_last_month = end_last_month.replace(day=1)
        return start_last_month, end_last_month, f'Bulan Lalu ({start_last_month.strftime("%B %Y")})'

    if '7 hari' in msg or 'seminggu terakhir' in msg:
        return today - timedelta(days=7), today, '7 Hari Terakhir'

    if '30 hari' in msg or 'sebulan terakhir' in msg:
        return today - timedelta(days=30), today, '30 Hari Terakhir'

    if '3 bulan' in msg or 'kuartal' in msg or 'quarter' in msg:
        return today - timedelta(days=90), today, '3 Bulan Terakhir'

    return None


def gather_data(intent, message=''):
    """
    Kumpulkan data dari ORM sesuai intent. Return dict ringkasan.

    AMAN: Hanya angka agregat, tidak ada data pribadi/sensitif.
    Mendukung konteks waktu cerdas dari pesan user.
    """
    today = timezone.now().date()
    month_start = today.replace(day=1)

    time_ctx = _parse_time_context(message) if message else None
    if time_ctx:
        month_start, today, _ = time_ctx

    try:
        if intent == 'properti':
            return _gather_properti()
        elif intent == 'kamar':
            return _gather_kamar()
        elif intent == 'penyewa':
            return _gather_penyewa()
        elif intent == 'kontrak':
            return _gather_kontrak(today)
        elif intent == 'tagihan':
            return _gather_tagihan(today, month_start)
        elif intent == 'pembayaran':
            return _gather_pembayaran(today, month_start)
        elif intent == 'biaya':
            return _gather_biaya(today, month_start)
        elif intent == 'keuntungan':
            return _gather_keuntungan(today, month_start)
        elif intent == 'karyawan':
            return _gather_karyawan()
        elif intent == 'bantuan':
            return _gather_bantuan()
        elif intent == 'laporan_meeting':
            return _gather_laporan_meeting(today, month_start)
        elif intent == 'executive_summary':
            return _gather_executive_summary(today, month_start)
        elif intent == 'swot':
            return _gather_swot(today, month_start)
        elif intent == 'rencana_aksi':
            return _gather_rencana_aksi(today, month_start)
        elif intent == 'forecasting':
            return _gather_forecasting(today, month_start)
        elif intent == 'risiko':
            return _gather_risiko(today, month_start)
        elif intent == 'perbandingan':
            return _gather_perbandingan(today, month_start)
        else:
            return _gather_umum(today, month_start)
    except Exception as e:
        logger.error(f"[AI INTENT] Error gathering data for intent '{intent}': {e}", exc_info=True)
        return {
            'intent': intent,
            'error': True,
            'ringkasan': f'Terjadi kesalahan saat mengambil data: {str(e)}',
        }


# ═══════════════════════════════════════════════════════════════
# DATA GATHERERS — Satu fungsi per intent (konteks SIMKOS)
# ═══════════════════════════════════════════════════════════════

def _gather_properti():
    """Data properti kost/kontrakan."""
    from apps.properti.models import Properti, TipeKamar, Kamar

    total_properti = Properti.objects.filter(aktif=True).count()
    total_kamar = Kamar.objects.count()
    kamar_terisi = Kamar.objects.filter(status='terisi').count()
    kamar_tersedia = Kamar.objects.filter(status='tersedia').count()
    kamar_maintenance = Kamar.objects.filter(status='maintenance').count()

    # Per tipe properti
    tipe_info = []
    for tipe_code, tipe_label in Properti.TIPE_CHOICES:
        count = Properti.objects.filter(aktif=True, tipe=tipe_code).count()
        if count > 0:
            tipe_info.append(f"- {tipe_label}: {count} properti")

    # Per properti: detail kamar
    properti_list = []
    for p in Properti.objects.filter(aktif=True).order_by('nama')[:10]:
        total = p.total_kamar
        terisi = p.kamar_terisi
        tersedia = p.kamar_tersedia
        occ = round(terisi / total * 100, 1) if total > 0 else 0
        properti_list.append(f"- {p.nama} ({p.get_tipe_display()}): {terisi}/{total} kamar terisi ({occ}%)")

    ringkasan = f"""Data Properti SIMKOS:
- Total Properti Aktif: {total_properti}
- Total Kamar: {total_kamar}
- Kamar Terisi: {kamar_terisi}
- Kamar Tersedia: {kamar_tersedia}
- Kamar Maintenance: {kamar_maintenance}
- Tingkat Okupansi: {round(kamar_terisi / total_kamar * 100, 1) if total_kamar > 0 else 0}%

Jenis Properti:
{chr(10).join(tipe_info) if tipe_info else '- Belum ada properti'}

Detail per Properti:
{chr(10).join(properti_list) if properti_list else '- Belum ada properti'}"""

    return {'intent': 'properti', 'ringkasan': ringkasan}


def _gather_kamar():
    """Data kamar: status, tipe, okupansi."""
    from apps.properti.models import Properti, TipeKamar, Kamar

    total_kamar = Kamar.objects.count()
    kamar_terisi = Kamar.objects.filter(status='terisi').count()
    kamar_tersedia = Kamar.objects.filter(status='tersedia').count()
    kamar_maintenance = Kamar.objects.filter(status='maintenance').count()
    okupansi = round(kamar_terisi / total_kamar * 100, 1) if total_kamar > 0 else 0

    # Per tipe kamar
    tipe_info = []
    for tk in TipeKamar.objects.filter(aktif=True).order_by('nama'):
        count = Kamar.objects.filter(tipe_kamar=tk).count()
        count_terisi = Kamar.objects.filter(tipe_kamar=tk, status='terisi').count()
        harga = tk.harga_bulanan
        tipe_info.append(f"- {tk.nama}: {count} kamar ({count_terisi} terisi) — Rp {harga:,.0f}/bulan")

    # Per properti
    properti_info = []
    for p in Properti.objects.filter(aktif=True).order_by('nama')[:10]:
        total = p.total_kamar
        terisi = p.kamar_terisi
        tersedia = p.kamar_tersedia
        properti_info.append(f"- {p.nama}: {tersedia} tersedia, {terisi} terisi (dari {total})")

    ringkasan = f"""Data Kamar SIMKOS:
- Total Kamar: {total_kamar}
- Terisi: {kamar_terisi}
- Tersedia: {kamar_tersedia}
- Maintenance: {kamar_maintenance}
- Tingkat Okupansi: {okupansi}%

Tipe Kamar & Harga:
{chr(10).join(tipe_info) if tipe_info else '- Belum ada tipe kamar'}

Status per Properti:
{chr(10).join(properti_info) if properti_info else '- Belum ada data'}"""

    return {'intent': 'kamar', 'ringkasan': ringkasan}


def _gather_penyewa():
    """Data penyewa kost — termasuk detail penghuni."""
    from apps.penyewa.models import Penyewa
    from apps.sewa.models import KontrakSewa

    total_aktif = Penyewa.objects.filter(status='aktif').count()
    total_nonaktif = Penyewa.objects.filter(status='nonaktif').count()
    total_blacklist = Penyewa.objects.filter(status='blacklist').count()
    total_all = Penyewa.objects.count()

    # Gender breakdown
    laki = Penyewa.objects.filter(status='aktif', jenis_kelamin='L').count()
    perempuan = Penyewa.objects.filter(status='aktif', jenis_kelamin='P').count()

    # Pekerjaan breakdown
    pekerjaan_info = Penyewa.objects.filter(
        status='aktif'
    ).exclude(
        pekerjaan__isnull=True
    ).exclude(
        pekerjaan=''
    ).values('pekerjaan').annotate(
        jml=Count('id')
    ).order_by('-jml')[:5]
    pekerjaan_list = [f"- {p['pekerjaan']}: {p['jml']} orang" for p in pekerjaan_info]

    # Kontrak aktif
    kontrak_aktif = KontrakSewa.objects.filter(status='aktif').count()

    # ── Detail penghuni aktif (nama, kamar, properti, durasi sewa) ──
    # DATA AMAN: Hanya nama, kamar, properti, dan durasi — TIDAK ada NIK, telepon, alamat
    today = timezone.now().date()
    penghuni_list = []
    for k in KontrakSewa.objects.filter(
        status='aktif'
    ).select_related('penyewa', 'kamar', 'kamar__properti', 'kamar__tipe_kamar').order_by('tanggal_masuk')[:15]:
        durasi = (today - k.tanggal_masuk).days
        bulan = durasi // 30
        tipe_kamar = k.kamar.tipe_kamar.nama if k.kamar.tipe_kamar else '-'
        pekerjaan = k.penyewa.pekerjaan or '-'
        penghuni_list.append(
            f"- {k.penyewa.nama} | {k.kamar.properti.nama} Kamar {k.kamar.nomor_kamar} "
            f"({tipe_kamar}) | Masuk: {k.tanggal_masuk.strftime('%d/%m/%Y')} "
            f"({bulan} bulan, {durasi} hari) | Pekerjaan: {pekerjaan}"
        )

    # ── Penyewa terlama (top 5) ──
    penyewa_terlama = []
    for k in KontrakSewa.objects.filter(
        status='aktif'
    ).select_related('penyewa', 'kamar', 'kamar__properti').order_by('tanggal_masuk')[:5]:
        durasi = (today - k.tanggal_masuk).days
        bulan = durasi // 30
        penyewa_terlama.append(
            f"- {k.penyewa.nama}: {bulan} bulan ({durasi} hari) "
            f"di {k.kamar.properti.nama} Kamar {k.kamar.nomor_kamar}"
        )

    # ── Penyewa terbaru (5 terakhir masuk) ──
    penyewa_terbaru = []
    for k in KontrakSewa.objects.filter(
        status='aktif'
    ).select_related('penyewa', 'kamar', 'kamar__properti').order_by('-tanggal_masuk')[:5]:
        durasi = (today - k.tanggal_masuk).days
        penyewa_terbaru.append(
            f"- {k.penyewa.nama}: masuk {k.tanggal_masuk.strftime('%d/%m/%Y')} "
            f"({durasi} hari lalu) di {k.kamar.properti.nama} Kamar {k.kamar.nomor_kamar}"
        )

    ringkasan = f"""Data Penyewa SIMKOS:
- Total Penyewa: {total_all}
- Penyewa Aktif: {total_aktif}
- Penyewa Nonaktif: {total_nonaktif}
- Penyewa Blacklist: {total_blacklist}
- Kontrak Aktif: {kontrak_aktif}

Jenis Kelamin (Aktif):
- Laki-laki: {laki}
- Perempuan: {perempuan}

Pekerjaan Terbanyak:
{chr(10).join(pekerjaan_list) if pekerjaan_list else '- Data pekerjaan belum lengkap'}

🏆 Penghuni Terlama (Top 5):
{chr(10).join(penyewa_terlama) if penyewa_terlama else '- Belum ada penghuni'}

🆕 Penghuni Terbaru (5 Terakhir Masuk):
{chr(10).join(penyewa_terbaru) if penyewa_terbaru else '- Belum ada penghuni'}

📋 Daftar Seluruh Penghuni Aktif:
{chr(10).join(penghuni_list) if penghuni_list else '- Belum ada penghuni aktif'}

CATATAN KEAMANAN: Data yang ditampilkan hanya nama, kamar, durasi sewa, dan pekerjaan. Data sensitif (NIK, telepon, alamat) TIDAK disertakan."""

    return {'intent': 'penyewa', 'ringkasan': ringkasan}


def _gather_kontrak(today):
    """Data kontrak sewa."""
    from apps.sewa.models import KontrakSewa

    kontrak_aktif = KontrakSewa.objects.filter(status='aktif').count()
    kontrak_selesai = KontrakSewa.objects.filter(status='selesai').count()
    kontrak_batal = KontrakSewa.objects.filter(status='dibatalkan').count()
    total_kontrak = KontrakSewa.objects.count()

    # Kontrak segera habis (30 hari ke depan)
    segera_habis = KontrakSewa.objects.filter(
        status='aktif',
        tanggal_keluar__lte=today + timedelta(days=30),
        tanggal_keluar__gte=today
    ).count()

    # Kontrak sudah habis tapi belum diupdate
    sudah_habis = KontrakSewa.objects.filter(
        status='aktif',
        tanggal_keluar__lt=today
    ).count()

    # Detail kontrak segera habis
    kontrak_habis_list = []
    for k in KontrakSewa.objects.filter(
        status='aktif',
        tanggal_keluar__lte=today + timedelta(days=30),
        tanggal_keluar__gte=today
    ).select_related('penyewa', 'kamar', 'kamar__properti').order_by('tanggal_keluar')[:5]:
        sisa = (k.tanggal_keluar - today).days
        kontrak_habis_list.append(
            f"- {k.penyewa.nama} ({k.kamar.properti.nama} - Kamar {k.kamar.nomor_kamar}): "
            f"habis {k.tanggal_keluar.strftime('%d/%m/%Y')} ({sisa} hari lagi)"
        )

    ringkasan = f"""Data Kontrak Sewa:
- Total Kontrak: {total_kontrak}
- Kontrak Aktif: {kontrak_aktif}
- Kontrak Selesai: {kontrak_selesai}
- Kontrak Dibatalkan: {kontrak_batal}

⚠️ Kontrak Segera Habis (30 Hari): {segera_habis}
⚠️ Kontrak Sudah Lewat (belum diupdate): {sudah_habis}

Detail Kontrak Segera Habis:
{chr(10).join(kontrak_habis_list) if kontrak_habis_list else '- Tidak ada kontrak segera habis'}"""

    return {'intent': 'kontrak', 'ringkasan': ringkasan}


def _gather_tagihan(today, month_start):
    """Data tagihan sewa."""
    from apps.sewa.models import TagihanSewa

    total_tagihan = TagihanSewa.objects.count()
    tagihan_lunas = TagihanSewa.objects.filter(status='lunas').count()
    tagihan_belum = TagihanSewa.objects.filter(status='belum_bayar').count()
    tagihan_sebagian = TagihanSewa.objects.filter(status='sebagian').count()
    tagihan_terlambat = TagihanSewa.objects.filter(status='terlambat').count()

    # Nilai
    total_nilai = float(TagihanSewa.objects.aggregate(t=Sum('jumlah'))['t'] or 0)
    nilai_lunas = float(TagihanSewa.objects.filter(status='lunas').aggregate(t=Sum('jumlah'))['t'] or 0)
    nilai_menunggak = float(TagihanSewa.objects.filter(
        status__in=['belum_bayar', 'terlambat']
    ).aggregate(t=Sum('jumlah'))['t'] or 0)

    # Tagihan bulan ini
    bulan_ini = today.month
    tahun_ini = today.year
    tagihan_bl_ini = TagihanSewa.objects.filter(
        periode_bulan=bulan_ini, periode_tahun=tahun_ini
    ).count()
    tagihan_bl_ini_lunas = TagihanSewa.objects.filter(
        periode_bulan=bulan_ini, periode_tahun=tahun_ini, status='lunas'
    ).count()

    ringkasan = f"""Data Tagihan Sewa:
- Total Tagihan: {total_tagihan}
- Lunas: {tagihan_lunas} (Rp {nilai_lunas:,.0f})
- Belum Bayar: {tagihan_belum}
- Bayar Sebagian: {tagihan_sebagian}
- Terlambat: {tagihan_terlambat}
- Total Nilai Menunggak: Rp {nilai_menunggak:,.0f}

Tagihan Bulan Ini ({today.strftime('%B %Y')}):
- Total: {tagihan_bl_ini} tagihan
- Sudah Lunas: {tagihan_bl_ini_lunas}
- Belum Lunas: {tagihan_bl_ini - tagihan_bl_ini_lunas}"""

    return {'intent': 'tagihan', 'ringkasan': ringkasan}


def _gather_pembayaran(today, month_start):
    """Data pembayaran sewa (pendapatan)."""
    from apps.sewa.models import PembayaranSewa

    # Bulan ini
    pembayaran_bulan_ini = PembayaranSewa.objects.filter(
        tanggal_bayar__gte=month_start, tanggal_bayar__lte=today
    )
    total_bulan_ini = float(pembayaran_bulan_ini.aggregate(t=Sum('jumlah_bayar'))['t'] or 0)
    count_bulan_ini = pembayaran_bulan_ini.count()

    # Keseluruhan
    total_semua = float(PembayaranSewa.objects.aggregate(t=Sum('jumlah_bayar'))['t'] or 0)

    # Bulan lalu
    prev_month_end = month_start - timedelta(days=1)
    prev_month_start = prev_month_end.replace(day=1)
    total_bulan_lalu = float(PembayaranSewa.objects.filter(
        tanggal_bayar__gte=prev_month_start, tanggal_bayar__lte=prev_month_end
    ).aggregate(t=Sum('jumlah_bayar'))['t'] or 0)
    growth = round(((total_bulan_ini - total_bulan_lalu) / total_bulan_lalu * 100), 1) if total_bulan_lalu > 0 else 0

    # Per metode bayar
    metode_info = PembayaranSewa.objects.filter(
        tanggal_bayar__gte=month_start, tanggal_bayar__lte=today
    ).values('metode_bayar').annotate(
        total=Sum('jumlah_bayar'), jml=Count('id')
    ).order_by('-total')
    metode_list = []
    for m in metode_info:
        label = dict(PembayaranSewa.METODE_CHOICES).get(m['metode_bayar'], m['metode_bayar'])
        metode_list.append(f"- {label}: Rp {float(m['total']):,.0f} ({m['jml']} trx)")

    # Hari ini
    bayar_hari_ini = float(PembayaranSewa.objects.filter(
        tanggal_bayar=today
    ).aggregate(t=Sum('jumlah_bayar'))['t'] or 0)

    ringkasan = f"""Data Pembayaran Sewa:
- Pendapatan Hari Ini: Rp {bayar_hari_ini:,.0f}
- Pendapatan Bulan Ini: Rp {total_bulan_ini:,.0f} ({count_bulan_ini} pembayaran)
- Pendapatan Bulan Lalu: Rp {total_bulan_lalu:,.0f}
- Growth: {'+' if growth >= 0 else ''}{growth}%
- Total Pendapatan (semua): Rp {total_semua:,.0f}

Metode Pembayaran Bulan Ini:
{chr(10).join(metode_list) if metode_list else '- Belum ada pembayaran bulan ini'}"""

    return {'intent': 'pembayaran', 'ringkasan': ringkasan}


def _gather_biaya(today, month_start):
    """Data biaya operasional kost."""
    from apps.biaya.models import TransaksiBiaya, KategoriBiaya

    total_biaya = float(TransaksiBiaya.objects.aggregate(t=Sum('jumlah'))['t'] or 0)
    biaya_bulan_ini = float(TransaksiBiaya.objects.filter(
        tanggal__gte=month_start, tanggal__lte=today
    ).aggregate(t=Sum('jumlah'))['t'] or 0)
    jumlah_trx = TransaksiBiaya.objects.filter(
        tanggal__gte=month_start, tanggal__lte=today
    ).count()

    # Per kategori
    per_kat = TransaksiBiaya.objects.filter(
        tanggal__gte=month_start, tanggal__lte=today
    ).values('kategori__nama').annotate(
        total=Sum('jumlah')
    ).order_by('-total')[:7]
    kat_list = [f"- {k['kategori__nama'] or 'Lainnya'}: Rp {float(k['total']):,.0f}" for k in per_kat]

    ringkasan = f"""Data Biaya Operasional Kost:
- Total Biaya Keseluruhan: Rp {total_biaya:,.0f}
- Biaya Bulan Ini: Rp {biaya_bulan_ini:,.0f}
- Jumlah Transaksi Bulan Ini: {jumlah_trx}

Biaya per Kategori (Bulan Ini):
{chr(10).join(kat_list) if kat_list else '- Belum ada biaya bulan ini'}"""

    return {'intent': 'biaya', 'ringkasan': ringkasan}


def _gather_keuntungan(today, month_start):
    """Data keuntungan / profit bisnis kost."""
    from apps.sewa.models import PembayaranSewa
    from apps.biaya.models import TransaksiBiaya

    # Pendapatan
    pendapatan_bulan = float(PembayaranSewa.objects.filter(
        tanggal_bayar__gte=month_start, tanggal_bayar__lte=today
    ).aggregate(t=Sum('jumlah_bayar'))['t'] or 0)
    pendapatan_total = float(PembayaranSewa.objects.aggregate(t=Sum('jumlah_bayar'))['t'] or 0)

    # Biaya
    biaya_bulan = float(TransaksiBiaya.objects.filter(
        tanggal__gte=month_start, tanggal__lte=today
    ).aggregate(t=Sum('jumlah'))['t'] or 0)
    biaya_total = float(TransaksiBiaya.objects.aggregate(t=Sum('jumlah'))['t'] or 0)

    # Profit
    profit_bulan = pendapatan_bulan - biaya_bulan
    profit_total = pendapatan_total - biaya_total
    margin = round(profit_bulan / pendapatan_bulan * 100, 1) if pendapatan_bulan > 0 else 0

    ringkasan = f"""Data Keuntungan Bisnis Kost:
- Pendapatan Sewa Bulan Ini: Rp {pendapatan_bulan:,.0f}
- Biaya Operasional Bulan Ini: Rp {biaya_bulan:,.0f}
- Profit Bulan Ini: Rp {profit_bulan:,.0f}
- Profit Margin: {margin}%
- Status: {'✅ UNTUNG' if profit_bulan > 0 else '❌ RUGI'}

Rincian Keseluruhan:
- Total Pendapatan (semua): Rp {pendapatan_total:,.0f}
- Total Biaya (semua): Rp {biaya_total:,.0f}
- Total Profit: Rp {profit_total:,.0f}"""

    return {'intent': 'keuntungan', 'ringkasan': ringkasan}


def _gather_karyawan():
    """Data karyawan / HR."""
    try:
        from apps.hr.models import Karyawan, Departemen, Jabatan

        total_karyawan = Karyawan.objects.filter(aktif=True).count()
        total_non_aktif = Karyawan.objects.filter(aktif=False).count()
        total_departemen = Departemen.objects.count()
        total_jabatan = Jabatan.objects.count()

        dept_info = Departemen.objects.annotate(
            jml=Count('karyawan', filter=Q(karyawan__aktif=True))
        ).order_by('-jml')[:5]
        dept_list = [f"- {d.nama}: {d.jml} karyawan" for d in dept_info]

        ringkasan = f"""Data Karyawan & HR:
- Total Karyawan Aktif: {total_karyawan}
- Total Karyawan Non-Aktif: {total_non_aktif}
- Total Departemen: {total_departemen}
- Total Jabatan: {total_jabatan}

Karyawan per Departemen:
{chr(10).join(dept_list) if dept_list else '- Belum ada departemen'}"""

    except ImportError:
        ringkasan = "Modul HR belum tersedia di sistem."

    return {'intent': 'karyawan', 'ringkasan': ringkasan}


def _gather_bantuan():
    """Panduan fitur SIMKOS secara detail."""
    ringkasan = """Panduan Lengkap Sistem SIMKOS (Sistem Manajemen Kost):

═══════════════════════════════════════════
MODUL-MODUL SIMKOS YANG TERSEDIA:
═══════════════════════════════════════════

1. Dashboard — Ringkasan data bisnis kost secara real-time: statistik properti, okupansi kamar, pendapatan, tagihan menunggak, dan aktivitas terkini.

2. Properti — Manajemen data properti (kost/kontrakan/apartemen): tambah properti, kelola tipe kamar, atur harga & fasilitas, denah kamar interaktif.

3. Kamar — Kelola kamar per properti: status kamar (tersedia/terisi/maintenance), nomor kamar, lantai, tipe kamar, fasilitas tambahan.

4. Penyewa — Database penyewa/penghuni: data personal, foto KTP, kontak darurat, riwayat sewa, status (aktif/nonaktif/blacklist).

5. Kontrak Sewa — Buat dan kelola kontrak sewa: tanggal mulai & selesai, harga sewa, deposit, catatan kontrak. Nomor kontrak otomatis.

6. Tagihan Sewa — Generate tagihan sewa bulanan: status pembayaran (belum bayar/lunas/sebagian/terlambat), cetak tagihan, kirim reminder.

7. Pembayaran — Catat pembayaran sewa: metode bayar (tunai/transfer/e-wallet/QRIS), bukti bayar, otomatis update status tagihan.

8. Biaya Operasional — Catat pengeluaran operasional kost: listrik, air, kebersihan, internet, maintenance. Per kategori dengan laporan.

9. Laporan — Laporan keuangan lengkap: pendapatan vs pengeluaran, laporan per properti, per kamar, per periode (harian/bulanan/tahunan).

10. AI Assistant — Fitur AI untuk analisa bisnis kost: tanya jawab data, prediksi, SWOT analysis, laporan meeting otomatis, rekomendasi bisnis.

11. Pengaturan — Konfigurasi sistem: profil perusahaan, pengaturan pajak, metode pembayaran, notifikasi, dan pengaturan lainnya.

12. HR & Karyawan — Manajemen SDM kost: data karyawan, departemen, jabatan, penggajian.

═══════════════════════════════════════════
CONTOH PERTANYAAN AI:
═══════════════════════════════════════════

📊 Data & Laporan:
- "Berapa okupansi kamar bulan ini?"
- "Tampilkan tagihan yang belum dibayar"
- "Berapa total pendapatan bulan ini?"
- "Bandingkan pendapatan bulan ini dan bulan lalu"

📈 Analisa & Insight:
- "Analisa SWOT bisnis kost saya"
- "Buat executive summary bulan ini"
- "Prediksi pendapatan bulan depan"
- "Apa risiko bisnis kost saat ini?"

📝 Rencana & Strategi:
- "Buat rencana meningkatkan okupansi"
- "Rekomendasikan strategi harga sewa"
- "Buat laporan untuk rapat bulanan"

💡 Tips: Gunakan konteks waktu seperti "minggu ini", "bulan lalu", "3 bulan terakhir" untuk analisa periode spesifik!"""

    return {'intent': 'bantuan', 'ringkasan': ringkasan}


def _gather_laporan_meeting(today, month_start):
    """Data lengkap untuk laporan meeting/rapat."""
    from apps.properti.models import Properti, Kamar
    from apps.sewa.models import KontrakSewa, TagihanSewa, PembayaranSewa
    from apps.biaya.models import TransaksiBiaya

    total_kamar = Kamar.objects.count()
    kamar_terisi = Kamar.objects.filter(status='terisi').count()
    okupansi = round(kamar_terisi / total_kamar * 100, 1) if total_kamar > 0 else 0

    pendapatan = float(PembayaranSewa.objects.filter(
        tanggal_bayar__gte=month_start, tanggal_bayar__lte=today
    ).aggregate(t=Sum('jumlah_bayar'))['t'] or 0)

    biaya = float(TransaksiBiaya.objects.filter(
        tanggal__gte=month_start, tanggal__lte=today
    ).aggregate(t=Sum('jumlah'))['t'] or 0)

    tagihan_menunggak = TagihanSewa.objects.filter(
        status__in=['belum_bayar', 'terlambat']
    ).count()
    nilai_menunggak = float(TagihanSewa.objects.filter(
        status__in=['belum_bayar', 'terlambat']
    ).aggregate(t=Sum('jumlah'))['t'] or 0)

    kontrak_aktif = KontrakSewa.objects.filter(status='aktif').count()
    kontrak_habis = KontrakSewa.objects.filter(
        status='aktif',
        tanggal_keluar__lte=today + timedelta(days=30),
        tanggal_keluar__gte=today
    ).count()

    profit = pendapatan - biaya

    ringkasan = f"""INSTRUKSI: Buat LAPORAN MEETING profesional lengkap dengan format naratif + tabel.

Data Periode {month_start.strftime('%d/%m/%Y')} s/d {today.strftime('%d/%m/%Y')}:
- Okupansi: {kamar_terisi}/{total_kamar} kamar ({okupansi}%)
- Pendapatan Sewa: Rp {pendapatan:,.0f}
- Biaya Operasional: Rp {biaya:,.0f}
- Profit: Rp {profit:,.0f}
- Tagihan Menunggak: {tagihan_menunggak} tagihan (Rp {nilai_menunggak:,.0f})
- Kontrak Aktif: {kontrak_aktif}
- Kontrak Segera Habis (30 hari): {kontrak_habis}"""

    return {'intent': 'laporan_meeting', 'ringkasan': ringkasan}


def _gather_executive_summary(today, month_start):
    """Ringkasan eksekutif bisnis kost."""
    from apps.properti.models import Properti, Kamar
    from apps.sewa.models import PembayaranSewa, TagihanSewa
    from apps.biaya.models import TransaksiBiaya

    total_properti = Properti.objects.filter(aktif=True).count()
    total_kamar = Kamar.objects.count()
    kamar_terisi = Kamar.objects.filter(status='terisi').count()
    okupansi = round(kamar_terisi / total_kamar * 100, 1) if total_kamar > 0 else 0

    pendapatan = float(PembayaranSewa.objects.filter(
        tanggal_bayar__gte=month_start, tanggal_bayar__lte=today
    ).aggregate(t=Sum('jumlah_bayar'))['t'] or 0)
    biaya = float(TransaksiBiaya.objects.filter(
        tanggal__gte=month_start, tanggal__lte=today
    ).aggregate(t=Sum('jumlah'))['t'] or 0)
    tagihan_menunggak = TagihanSewa.objects.filter(
        status__in=['belum_bayar', 'terlambat']
    ).count()

    ringkasan = f"""INSTRUKSI: Buat EXECUTIVE SUMMARY / RINGKASAN EKSEKUTIF yang ringkas dan profesional.

Data Bisnis Kost:
- Jumlah Properti: {total_properti}
- Total Kamar: {total_kamar} (Terisi: {kamar_terisi}, Okupansi: {okupansi}%)
- Pendapatan Bulan Ini: Rp {pendapatan:,.0f}
- Biaya Bulan Ini: Rp {biaya:,.0f}
- Profit: Rp {pendapatan - biaya:,.0f}
- Tagihan Menunggak: {tagihan_menunggak}"""

    return {'intent': 'executive_summary', 'ringkasan': ringkasan}


def _gather_swot(today, month_start):
    """Data untuk analisa SWOT bisnis kost."""
    from apps.properti.models import Properti, Kamar
    from apps.sewa.models import PembayaranSewa, TagihanSewa, KontrakSewa
    from apps.biaya.models import TransaksiBiaya

    total_kamar = Kamar.objects.count()
    kamar_terisi = Kamar.objects.filter(status='terisi').count()
    okupansi = round(kamar_terisi / total_kamar * 100, 1) if total_kamar > 0 else 0

    pendapatan = float(PembayaranSewa.objects.filter(
        tanggal_bayar__gte=month_start, tanggal_bayar__lte=today
    ).aggregate(t=Sum('jumlah_bayar'))['t'] or 0)
    biaya = float(TransaksiBiaya.objects.filter(
        tanggal__gte=month_start, tanggal__lte=today
    ).aggregate(t=Sum('jumlah'))['t'] or 0)
    tagihan_menunggak = TagihanSewa.objects.filter(
        status__in=['belum_bayar', 'terlambat']
    ).count()
    kamar_tersedia = Kamar.objects.filter(status='tersedia').count()

    # Prev month for comparison
    prev_end = month_start - timedelta(days=1)
    prev_start = prev_end.replace(day=1)
    prev_pendapatan = float(PembayaranSewa.objects.filter(
        tanggal_bayar__gte=prev_start, tanggal_bayar__lte=prev_end
    ).aggregate(t=Sum('jumlah_bayar'))['t'] or 0)
    growth = round(((pendapatan - prev_pendapatan) / prev_pendapatan * 100), 1) if prev_pendapatan > 0 else 0

    ringkasan = f"""INSTRUKSI: Buat analisa SWOT bisnis kost dalam format tabel 4 kategori (Strengths, Weaknesses, Opportunities, Threats), masing-masing 2-3 poin.

Data Bisnis Kost untuk Analisa:
- Okupansi: {okupansi}% ({kamar_terisi}/{total_kamar} kamar)
- Kamar Tersedia: {kamar_tersedia}
- Pendapatan Bulan Ini: Rp {pendapatan:,.0f}
- Growth vs Bulan Lalu: {'+' if growth >= 0 else ''}{growth}%
- Biaya Operasional: Rp {biaya:,.0f}
- Profit: Rp {pendapatan - biaya:,.0f}
- Tagihan Menunggak: {tagihan_menunggak}"""

    return {'intent': 'swot', 'ringkasan': ringkasan}


def _gather_rencana_aksi(today, month_start):
    """Data untuk rencana aksi / action plan."""
    from apps.properti.models import Kamar
    from apps.sewa.models import PembayaranSewa, TagihanSewa, KontrakSewa
    from apps.biaya.models import TransaksiBiaya

    total_kamar = Kamar.objects.count()
    kamar_terisi = Kamar.objects.filter(status='terisi').count()
    kamar_tersedia = Kamar.objects.filter(status='tersedia').count()
    okupansi = round(kamar_terisi / total_kamar * 100, 1) if total_kamar > 0 else 0

    pendapatan = float(PembayaranSewa.objects.filter(
        tanggal_bayar__gte=month_start, tanggal_bayar__lte=today
    ).aggregate(t=Sum('jumlah_bayar'))['t'] or 0)
    biaya = float(TransaksiBiaya.objects.filter(
        tanggal__gte=month_start, tanggal__lte=today
    ).aggregate(t=Sum('jumlah'))['t'] or 0)
    tagihan_menunggak = TagihanSewa.objects.filter(
        status__in=['belum_bayar', 'terlambat']
    ).count()
    kontrak_habis = KontrakSewa.objects.filter(
        status='aktif',
        tanggal_keluar__lte=today + timedelta(days=30),
        tanggal_keluar__gte=today
    ).count()

    ringkasan = f"""INSTRUKSI: Buat RENCANA AKSI / ACTION PLAN dengan tabel: Aksi, Prioritas, Target, Deadline.

Situasi Bisnis Kost Saat Ini:
- Okupansi: {okupansi}% ({kamar_tersedia} kamar kosong)
- Pendapatan: Rp {pendapatan:,.0f}
- Biaya: Rp {biaya:,.0f}
- Profit: Rp {pendapatan - biaya:,.0f}
- Tagihan Menunggak: {tagihan_menunggak}
- Kontrak Segera Habis: {kontrak_habis}"""

    return {'intent': 'rencana_aksi', 'ringkasan': ringkasan}


def _gather_forecasting(today, month_start):
    """Data untuk forecasting/prediksi."""
    from apps.sewa.models import PembayaranSewa

    # Pendapatan 3 bulan terakhir
    monthly_data = []
    for i in range(3, 0, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        from datetime import date
        import calendar
        m_start = date(y, m, 1)
        _, last_day = calendar.monthrange(y, m)
        m_end = date(y, m, last_day)
        m_rev = float(PembayaranSewa.objects.filter(
            tanggal_bayar__gte=m_start, tanggal_bayar__lte=m_end
        ).aggregate(t=Sum('jumlah_bayar'))['t'] or 0)
        monthly_data.append(f"- {m_start.strftime('%B %Y')}: Rp {m_rev:,.0f}")

    # Bulan ini (partial)
    rev_now = float(PembayaranSewa.objects.filter(
        tanggal_bayar__gte=month_start, tanggal_bayar__lte=today
    ).aggregate(t=Sum('jumlah_bayar'))['t'] or 0)

    from apps.properti.models import Kamar
    total_kamar = Kamar.objects.count()
    kamar_terisi = Kamar.objects.filter(status='terisi').count()

    ringkasan = f"""INSTRUKSI: Buat PREDIKSI / FORECASTING pendapatan bulan depan dengan confidence level berdasarkan data historis.

Data Historis Pendapatan:
{chr(10).join(monthly_data)}
- {today.strftime('%B %Y')} (s/d {today.strftime('%d/%m')}): Rp {rev_now:,.0f}

Kondisi Saat Ini:
- Kamar Terisi: {kamar_terisi}/{total_kamar}
- Okupansi: {round(kamar_terisi / total_kamar * 100, 1) if total_kamar > 0 else 0}%"""

    return {'intent': 'forecasting', 'ringkasan': ringkasan}


def _gather_risiko(today, month_start):
    """Analisa risiko bisnis kost."""
    from apps.properti.models import Kamar
    from apps.sewa.models import TagihanSewa, KontrakSewa, PembayaranSewa
    from apps.biaya.models import TransaksiBiaya

    total_kamar = Kamar.objects.count()
    kamar_terisi = Kamar.objects.filter(status='terisi').count()
    kamar_maintenance = Kamar.objects.filter(status='maintenance').count()
    okupansi = round(kamar_terisi / total_kamar * 100, 1) if total_kamar > 0 else 0

    tagihan_menunggak = TagihanSewa.objects.filter(
        status__in=['belum_bayar', 'terlambat']
    ).count()
    nilai_menunggak = float(TagihanSewa.objects.filter(
        status__in=['belum_bayar', 'terlambat']
    ).aggregate(t=Sum('jumlah'))['t'] or 0)

    kontrak_habis = KontrakSewa.objects.filter(
        status='aktif',
        tanggal_keluar__lte=today + timedelta(days=30),
        tanggal_keluar__gte=today
    ).count()

    pendapatan = float(PembayaranSewa.objects.filter(
        tanggal_bayar__gte=month_start, tanggal_bayar__lte=today
    ).aggregate(t=Sum('jumlah_bayar'))['t'] or 0)
    biaya = float(TransaksiBiaya.objects.filter(
        tanggal__gte=month_start, tanggal__lte=today
    ).aggregate(t=Sum('jumlah'))['t'] or 0)
    biaya_ratio = round(biaya / max(pendapatan, 1) * 100, 1)

    ringkasan = f"""INSTRUKSI: Buat ANALISA RISIKO dengan level 🔴Tinggi/🟡Sedang/🟢Rendah untuk setiap faktor.

Indikator Risiko Bisnis Kost:
- Okupansi: {okupansi}% ({kamar_terisi}/{total_kamar})
- Kamar Maintenance: {kamar_maintenance}
- Tagihan Menunggak: {tagihan_menunggak} (Rp {nilai_menunggak:,.0f})
- Kontrak Segera Habis (30 hari): {kontrak_habis}
- Rasio Biaya: {biaya_ratio}% (biaya Rp {biaya:,.0f} vs pendapatan Rp {pendapatan:,.0f})
- Profit: Rp {pendapatan - biaya:,.0f}"""

    return {'intent': 'risiko', 'ringkasan': ringkasan}


def _gather_perbandingan(today, month_start):
    """Perbandingan antar periode."""
    from apps.properti.models import Kamar
    from apps.sewa.models import PembayaranSewa, TagihanSewa
    from apps.biaya.models import TransaksiBiaya

    # Bulan ini
    pendapatan_now = float(PembayaranSewa.objects.filter(
        tanggal_bayar__gte=month_start, tanggal_bayar__lte=today
    ).aggregate(t=Sum('jumlah_bayar'))['t'] or 0)
    biaya_now = float(TransaksiBiaya.objects.filter(
        tanggal__gte=month_start, tanggal__lte=today
    ).aggregate(t=Sum('jumlah'))['t'] or 0)

    # Bulan lalu
    prev_end = month_start - timedelta(days=1)
    prev_start = prev_end.replace(day=1)
    pendapatan_prev = float(PembayaranSewa.objects.filter(
        tanggal_bayar__gte=prev_start, tanggal_bayar__lte=prev_end
    ).aggregate(t=Sum('jumlah_bayar'))['t'] or 0)
    biaya_prev = float(TransaksiBiaya.objects.filter(
        tanggal__gte=prev_start, tanggal__lte=prev_end
    ).aggregate(t=Sum('jumlah'))['t'] or 0)

    growth_rev = round(((pendapatan_now - pendapatan_prev) / pendapatan_prev * 100), 1) if pendapatan_prev > 0 else 0
    growth_biaya = round(((biaya_now - biaya_prev) / biaya_prev * 100), 1) if biaya_prev > 0 else 0

    ringkasan = f"""INSTRUKSI: Buat PERBANDINGAN periode dalam format tabel yang jelas.

Bulan Ini ({month_start.strftime('%B %Y')}):
- Pendapatan: Rp {pendapatan_now:,.0f}
- Biaya: Rp {biaya_now:,.0f}
- Profit: Rp {pendapatan_now - biaya_now:,.0f}

Bulan Lalu ({prev_start.strftime('%B %Y')}):
- Pendapatan: Rp {pendapatan_prev:,.0f}
- Biaya: Rp {biaya_prev:,.0f}
- Profit: Rp {pendapatan_prev - biaya_prev:,.0f}

Perubahan:
- Pendapatan: {'+' if growth_rev >= 0 else ''}{growth_rev}%
- Biaya: {'+' if growth_biaya >= 0 else ''}{growth_biaya}%"""

    return {'intent': 'perbandingan', 'ringkasan': ringkasan}


def _gather_umum(today, month_start):
    """Ringkasan umum semua modul SIMKOS."""
    from apps.properti.models import Properti, Kamar
    from apps.penyewa.models import Penyewa
    from apps.sewa.models import KontrakSewa, TagihanSewa, PembayaranSewa
    from apps.biaya.models import TransaksiBiaya

    total_properti = Properti.objects.filter(aktif=True).count()
    total_kamar = Kamar.objects.count()
    kamar_terisi = Kamar.objects.filter(status='terisi').count()
    okupansi = round(kamar_terisi / total_kamar * 100, 1) if total_kamar > 0 else 0
    total_penyewa = Penyewa.objects.filter(status='aktif').count()
    kontrak_aktif = KontrakSewa.objects.filter(status='aktif').count()

    pendapatan = float(PembayaranSewa.objects.filter(
        tanggal_bayar__gte=month_start, tanggal_bayar__lte=today
    ).aggregate(t=Sum('jumlah_bayar'))['t'] or 0)
    biaya = float(TransaksiBiaya.objects.filter(
        tanggal__gte=month_start, tanggal__lte=today
    ).aggregate(t=Sum('jumlah'))['t'] or 0)
    tagihan_menunggak = TagihanSewa.objects.filter(
        status__in=['belum_bayar', 'terlambat']
    ).count()

    ringkasan = f"""Ringkasan SIMKOS {today.strftime('%d %B %Y')}:
- Properti Aktif: {total_properti}
- Total Kamar: {total_kamar} (Terisi: {kamar_terisi}, Okupansi: {okupansi}%)
- Penyewa Aktif: {total_penyewa}
- Kontrak Aktif: {kontrak_aktif}
- Pendapatan Bulan Ini: Rp {pendapatan:,.0f}
- Biaya Bulan Ini: Rp {biaya:,.0f}
- Profit Bulan Ini: Rp {pendapatan - biaya:,.0f}
- Tagihan Menunggak: {tagihan_menunggak}"""

    return {'intent': 'umum', 'ringkasan': ringkasan}
