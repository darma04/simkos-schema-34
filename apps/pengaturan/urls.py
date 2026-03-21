"""
PENGATURAN URLS - Routing URL Pengaturan SIMKOS
"""
from django.urls import path
from . import views

app_name = 'pengaturan'

urlpatterns = [
    path('profil/', views.ProfilView.as_view(), name='profil'),
    path('perusahaan/', views.PerusahaanView.as_view(), name='perusahaan'),

    # Template Cetak
    path('template-cetak/', views.TemplateCetakListView.as_view(), name='template_cetak_list'),
    path('template-cetak/tambah/', views.TemplateCetakCreateView.as_view(), name='template_cetak_create'),
    path('template-cetak/<int:pk>/edit/', views.TemplateCetakUpdateView.as_view(), name='template_cetak_update'),

    # Manajemen Data
    path('manajemen-data/', views.ManajemenDataView.as_view(), name='manajemen_data'),
    path('manajemen-data/backup/', views.backup_data, name='backup_data'),
    path('manajemen-data/restore/', views.restore_data, name='restore_data'),
    path('manajemen-data/reset/', views.reset_data, name='reset_data'),
    path('manajemen-data/riwayat/<int:pk>/hapus/', views.hapus_riwayat_backup, name='hapus_riwayat_backup'),
    path('manajemen-data/bersihkan-log-aktivitas/', views.bersihkan_log_aktivitas, name='bersihkan_log_aktivitas'),
    path('manajemen-data/bersihkan-log-notifikasi/', views.bersihkan_log_notifikasi, name='bersihkan_log_notifikasi'),
    path('manajemen-data/api/db-stats/', views.db_stats_api, name='db_stats_api'),

    # Metode Pembayaran
    path('metode-pembayaran/', views.MetodePembayaranListView.as_view(), name='metode_pembayaran_list'),
    path('metode-pembayaran/tambah/', views.MetodePembayaranCreateView.as_view(), name='metode_pembayaran_create'),
    path('metode-pembayaran/<int:pk>/edit/', views.MetodePembayaranUpdateView.as_view(), name='metode_pembayaran_update'),
    path('metode-pembayaran/<int:pk>/', views.MetodePembayaranDetailView.as_view(), name='metode_pembayaran_detail'),
    path('metode-pembayaran/<int:pk>/delete/', views.metode_pembayaran_delete, name='metode_pembayaran_delete'),
]
