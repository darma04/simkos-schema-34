"""
SEWA URLS - Routing URL untuk modul Sewa (Kontrak, Tagihan, Pembayaran)
"""
from django.urls import path
from . import views

app_name = 'sewa'

urlpatterns = [
    # Kontrak Sewa
    path('kontrak/', views.KontrakSewaListView.as_view(), name='kontrak_list'),
    path('kontrak/add/', views.KontrakSewaCreateView.as_view(), name='kontrak_add'),
    path('kontrak/<int:pk>/', views.KontrakSewaDetailView.as_view(), name='kontrak_detail'),
    path('kontrak/<int:pk>/edit/', views.KontrakSewaUpdateView.as_view(), name='kontrak_edit'),
    path('kontrak/<int:pk>/delete/', views.KontrakSewaDeleteView.as_view(), name='kontrak_delete'),

    # Tagihan Sewa
    path('tagihan/', views.TagihanSewaListView.as_view(), name='tagihan_list'),
    path('tagihan/add/', views.TagihanSewaCreateView.as_view(), name='tagihan_add'),
    path('tagihan/<int:pk>/edit/', views.TagihanSewaUpdateView.as_view(), name='tagihan_edit'),
    path('tagihan/<int:pk>/delete/', views.TagihanSewaDeleteView.as_view(), name='tagihan_delete'),
    path('tagihan/<int:pk>/cetak/', views.TagihanCetakView.as_view(), name='tagihan_cetak'),

    # Pembayaran Sewa
    path('pembayaran/', views.PembayaranSewaListView.as_view(), name='pembayaran_list'),
    path('pembayaran/add/', views.PembayaranSewaCreateView.as_view(), name='pembayaran_add'),
    path('pembayaran/<int:pk>/', views.PembayaranDetailView.as_view(), name='pembayaran_detail'),
    path('pembayaran/<int:pk>/cetak/', views.PembayaranCetakView.as_view(), name='pembayaran_cetak'),
    path('pembayaran/<int:pk>/delete/', views.PembayaranSewaDeleteView.as_view(), name='pembayaran_delete'),
]
