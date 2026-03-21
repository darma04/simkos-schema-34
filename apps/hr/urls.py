"""
==========================================================================
 HR URLS - Routing URL untuk modul HR (SDM)
==========================================================================
 app_name = 'hr' → Namespace URL

 Grup URL:
 1. Dashboard HR → /hr/
 2. Departemen CRUD → /hr/departemen/...
 3. Jabatan CRUD → /hr/jabatan/...
 4. Karyawan CRUD → /hr/karyawan/...
 5. Absensi CRUD + Clock In/Out → /hr/absensi/...
 6. Penggajian CRUD + Generate → /hr/penggajian/...
 7. Face Recognition API → /hr/absensi/registrasi-wajah/...
 8. Pengaturan Absensi CRUD → /hr/pengaturan-absensi/...
==========================================================================
"""

from django.urls import path
from apps.hr import views

app_name = 'hr'  # Namespace URL

urlpatterns = [
    # Dashboard HR
    path('', views.DashboardHRView.as_view(), name='dashboard'),
    
    # Departemen CRUD
    path('departemen/', views.DepartemenListView.as_view(), name='departemen'),
    path('departemen/add/', views.DepartemenCreateView.as_view(), name='departemen-add'),
    path('departemen/<int:pk>/edit/', views.DepartemenUpdateView.as_view(), name='departemen-edit'),
    path('departemen/<int:pk>/delete/', views.DepartemenDeleteView.as_view(), name='departemen-delete'),
    
    # Jabatan CRUD
    path('jabatan/', views.JabatanListView.as_view(), name='jabatan'),
    path('jabatan/add/', views.JabatanCreateView.as_view(), name='jabatan-add'),
    path('jabatan/<int:pk>/edit/', views.JabatanUpdateView.as_view(), name='jabatan-edit'),
    path('jabatan/<int:pk>/delete/', views.JabatanDeleteView.as_view(), name='jabatan-delete'),
    
    # Karyawan CRUD
    path('karyawan/', views.KaryawanListView.as_view(), name='karyawan'),
    path('karyawan/add/', views.KaryawanCreateView.as_view(), name='karyawan-add'),
    path('karyawan/<int:pk>/', views.KaryawanDetailView.as_view(), name='karyawan-detail'),
    path('karyawan/<int:pk>/edit/', views.KaryawanUpdateView.as_view(), name='karyawan-edit'),
    path('karyawan/<int:pk>/delete/', views.KaryawanDeleteView.as_view(), name='karyawan-delete'),
    
    # Absensi CRUD
    path('absensi/', views.AbsensiListView.as_view(), name='absensi'),
    path('absensi/add/', views.AbsensiCreateView.as_view(), name='absensi-add'),
    path('absensi/<int:pk>/edit/', views.AbsensiUpdateView.as_view(), name='absensi-edit'),
    path('absensi/<int:pk>/delete/', views.AbsensiDeleteView.as_view(), name='absensi-delete'),
    path('absensi/deteksi-wajah/', views.AbsensiDeteksiWajahView.as_view(), name='absensi-deteksi-wajah'),
    path('absensi/clock-in/', views.absensi_clock_in, name='absensi-clock-in'),
    path('absensi/clock-out/', views.absensi_clock_out, name='absensi-clock-out'),
    
    # Penggajian CRUD
    path('penggajian/', views.PenggajianListView.as_view(), name='penggajian'),
    path('penggajian/add/', views.PenggajianCreateView.as_view(), name='penggajian-add'),
    path('penggajian/generate/', views.GeneratePenggajianView.as_view(), name='penggajian-generate'),
    path('penggajian/<int:pk>/', views.PenggajianDetailView.as_view(), name='penggajian-detail'),
    path('penggajian/<int:pk>/edit/', views.PenggajianUpdateView.as_view(), name='penggajian-edit'),
    path('penggajian/<int:pk>/delete/', views.PenggajianDeleteView.as_view(), name='penggajian-delete'),
    path('penggajian/<int:pk>/status/', views.PenggajianUpdateStatusView.as_view(), name='penggajian-status'),
    path('penggajian/<int:pk>/print/', views.PenggajianPrintView.as_view(), name='penggajian-print'),
    
    # Face Recognition
    path('absensi/registrasi-wajah/', views.RegistrasiWajahView.as_view(), name='registrasi-wajah'),
    path('absensi/registrasi-wajah/save/', views.save_face_encoding, name='save-face-encoding'),
    path('absensi/registrasi-wajah/<int:pk>/delete/', views.delete_face, name='delete-face'),
    path('absensi/detect-face/', views.detect_face_api, name='detect-face'),
    path('absensi/face-clock-in/', views.absensi_face_clock_in, name='absensi-face-clock-in'),
    path('absensi/face-clock-out/', views.absensi_face_clock_out, name='absensi-face-clock-out'),
    
    # Pengaturan Absensi
    path('pengaturan-absensi/', views.PengaturanAbsensiView.as_view(), name='pengaturan-absensi'),
    path('pengaturan-absensi/new/', views.PengaturanAbsensiCreateView.as_view(), name='pengaturan-absensi-new'),
    path('pengaturan-absensi/<int:pk>/edit/', views.PengaturanAbsensiUpdateView.as_view(), name='pengaturan-absensi-edit'),
    path('pengaturan-absensi/<int:pk>/delete/', views.pengaturan_absensi_delete, name='pengaturan-absensi-delete'),
    path('pengaturan-absensi/<int:pk>/activate/', views.pengaturan_absensi_activate, name='pengaturan-absensi-activate'),
]
