"""
==========================================================================
 AUTOMATION SIGNALS - Helper Notifikasi Telegram per Jenis Transaksi
==========================================================================
 File ini berisi fungsi-fungsi helper yang menyiapkan data notifikasi
 dan mengirimnya ke Telegram. Disebut "signals" karena awalnya dirancang
 sebagai signal handler, tapi sekarang DIPANGGIL LANGSUNG dari views.

 Alasan dipanggil dari views, bukan dari post_save signal:
 - Saat post_save terpicu, items transaksi belum tersimpan
 - Kita butuh data lengkap (items + total) sebelum kirim notifikasi
 - Jadi fungsi ini dipanggil SETELAH semua items disimpan di views

 Fungsi yang tersedia:
 ┌───────────────────────────────┬──────────────────────────────────────┐
 │ Fungsi                        │ Dipanggil dari                       │
 ├───────────────────────────────┼──────────────────────────────────────┤
 │ kirim_notifikasi_pos()        │ pos/views.py setelah transaksi POS   │
 │ kirim_notifikasi_sales_order()│ penjualan/views.py setelah SO dibuat │
 │ kirim_notifikasi_purchase_order()│ pembelian/views.py setelah PO dibuat│
 │ kirim_notifikasi_biaya()      │ biaya/views.py setelah biaya dibuat  │
 └───────────────────────────────┴──────────────────────────────────────┘

 Setiap fungsi:
 1. refresh_from_db() → Ambil data terbaru dari database
 2. Format detail items menjadi string untuk pesan
 3. Siapkan dict data sesuai placeholder template
 4. Panggil kirim_notifikasi_async() → kirim di background thread

 Terhubung dengan:
 - telegram_service.py → kirim_notifikasi_async(), format_angka()
 - views.py (pos, penjualan, pembelian, biaya) → Memanggil fungsi di sini
==========================================================================
"""
from .telegram_service import kirim_notifikasi_async, format_angka


def kirim_notifikasi_pos(instance):
    """Kirim notifikasi saat transaksi POS sudah lengkap (items + total sudah ada)"""
    # Refresh data dari database agar subtotal/total terbaru
    instance.refresh_from_db()
    
    items = instance.items.all()
    detail_items = ""
    for i, item in enumerate(items, 1):
        detail_items += f"  {i}. {item.produk.nama} x{item.jumlah} = Rp {format_angka(item.subtotal)}\n"
    
    if not detail_items:
        detail_items = "  (Belum ada item)"
    
    data = {
        'nomor_transaksi': instance.nomor_transaksi,
        'tanggal': instance.tanggal.strftime('%d/%m/%Y %H:%M') if instance.tanggal else '-',
        'kasir': instance.kasir.get_full_name() or instance.kasir.username if instance.kasir else '-',
        'gudang': str(instance.gudang) if instance.gudang else '-',
        'detail_items': detail_items.strip(),
        'subtotal': format_angka(instance.subtotal),
        'diskon': format_angka(instance.diskon),
        'pajak': format_angka(instance.pajak),
        'total': format_angka(instance.total_harga),
        'metode_pembayaran': str(instance.metode_pembayaran) if instance.metode_pembayaran else '-',
        'status': instance.get_status_display() if hasattr(instance, 'get_status_display') else instance.status,
        'customer': instance.nama_customer or 'Walk-in',
    }
    
    kirim_notifikasi_async('pos', instance.nomor_transaksi, data)


def kirim_notifikasi_sales_order(instance):
    """Kirim notifikasi saat Sales Order sudah lengkap (items + total sudah ada)"""
    instance.refresh_from_db()
    
    items = instance.items.all()
    detail_items = ""
    for i, item in enumerate(items, 1):
        detail_items += f"  {i}. {item.produk.nama} x{item.jumlah} = Rp {format_angka(item.subtotal)}\n"
    
    if not detail_items:
        detail_items = "  (Belum ada item)"
    
    data = {
        'nomor_so': instance.nomor_so,
        'tanggal': instance.tanggal.strftime('%d/%m/%Y %H:%M') if instance.tanggal else '-',
        'customer': str(instance.customer) if instance.customer else '-',
        'gudang': str(instance.gudang) if instance.gudang else '-',
        'detail_items': detail_items.strip(),
        'subtotal': format_angka(instance.subtotal),
        'diskon': format_angka(instance.diskon),
        'pajak': format_angka(instance.pajak),
        'total': format_angka(instance.total_harga),
        'status': instance.get_status_display() if hasattr(instance, 'get_status_display') else instance.status,
        'dibuat_oleh': instance.dibuat_oleh.get_full_name() or instance.dibuat_oleh.username if instance.dibuat_oleh else '-',
    }
    
    kirim_notifikasi_async('sales_order', instance.nomor_so, data)


def kirim_notifikasi_purchase_order(instance):
    """Kirim notifikasi saat Purchase Order sudah lengkap (items + total sudah ada)"""
    instance.refresh_from_db()
    
    items = instance.items.all()
    detail_items = ""
    for i, item in enumerate(items, 1):
        detail_items += f"  {i}. {item.produk.nama} x{item.jumlah} = Rp {format_angka(item.subtotal)}\n"
    
    if not detail_items:
        detail_items = "  (Belum ada item)"
    
    data = {
        'nomor_po': instance.nomor_po,
        'tanggal': instance.tanggal.strftime('%d/%m/%Y %H:%M') if instance.tanggal else '-',
        'supplier': str(instance.supplier) if instance.supplier else '-',
        'gudang': str(instance.gudang) if instance.gudang else '-',
        'detail_items': detail_items.strip(),
        'subtotal': format_angka(instance.subtotal),
        'pajak': format_angka(instance.pajak),
        'total': format_angka(instance.total_harga),
        'status': instance.get_status_display() if hasattr(instance, 'get_status_display') else instance.status,
        'dibuat_oleh': instance.dibuat_oleh.get_full_name() or instance.dibuat_oleh.username if instance.dibuat_oleh else '-',
    }
    
    kirim_notifikasi_async('purchase_order', instance.nomor_po, data)


def kirim_notifikasi_biaya(instance):
    """Kirim notifikasi saat Transaksi Biaya baru dibuat"""
    instance.refresh_from_db()
    
    data = {
        'nomor_transaksi': instance.nomor_transaksi,
        'tanggal': instance.tanggal.strftime('%d/%m/%Y') if instance.tanggal else '-',
        'kategori': str(instance.kategori) if instance.kategori else '-',
        'jumlah': format_angka(instance.jumlah),
        'deskripsi': instance.deskripsi or '-',
        'status': instance.get_status_display() if hasattr(instance, 'get_status_display') else instance.status,
        'dibuat_oleh': instance.dibuat_oleh.get_full_name() or instance.dibuat_oleh.username if instance.dibuat_oleh else '-',
        'metode_pembayaran': str(instance.metode_pembayaran) if instance.metode_pembayaran else '-',
    }
    
    kirim_notifikasi_async('biaya', instance.nomor_transaksi, data)
