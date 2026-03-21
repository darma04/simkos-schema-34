"""
LAPORAN URLS - URL Laporan SIMKOS
"""
from django.urls import path
from . import views

app_name = 'laporan'

urlpatterns = [
    path('pemasukan/', views.LaporanPemasukanView.as_view(), name='pemasukan'),
    path('pengeluaran/', views.LaporanPengeluaranView.as_view(), name='pengeluaran'),
    path('hunian/', views.LaporanHunianView.as_view(), name='hunian'),
    path('keuangan/', views.LaporanKeuanganView.as_view(), name='keuangan'),
]
