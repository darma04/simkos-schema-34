"""
PROPERTI URLS - Routing URL untuk modul Properti
"""
from django.urls import path
from . import views

app_name = 'properti'

urlpatterns = [
    # Properti CRUD
    path('', views.PropertiListView.as_view(), name='properti_list'),
    path('add/', views.PropertiCreateView.as_view(), name='properti_add'),
    path('<int:pk>/', views.PropertiDetailView.as_view(), name='properti_detail'),
    path('<int:pk>/edit/', views.PropertiUpdateView.as_view(), name='properti_edit'),
    path('<int:pk>/delete/', views.PropertiDeleteView.as_view(), name='properti_delete'),

    # Tipe Kamar CRUD
    path('tipe-kamar/', views.TipeKamarListView.as_view(), name='tipe_kamar_list'),
    path('tipe-kamar/add/', views.TipeKamarCreateView.as_view(), name='tipe_kamar_add'),
    path('tipe-kamar/<int:pk>/edit/', views.TipeKamarUpdateView.as_view(), name='tipe_kamar_edit'),
    path('tipe-kamar/<int:pk>/delete/', views.TipeKamarDeleteView.as_view(), name='tipe_kamar_delete'),

    # Kamar CRUD
    path('kamar/', views.KamarListView.as_view(), name='kamar_list'),
    path('kamar/add/', views.KamarCreateView.as_view(), name='kamar_add'),
    path('kamar/<int:pk>/edit/', views.KamarUpdateView.as_view(), name='kamar_edit'),
    path('kamar/<int:pk>/delete/', views.KamarDeleteView.as_view(), name='kamar_delete'),

    # Denah API
    path('api/kamar/<int:pk>/posisi/', views.denah_update_position, name='denah_update_position'),
    path('api/<int:properti_pk>/kamar/create/', views.denah_create_kamar, name='denah_create_kamar'),
    path('api/kamar/<int:pk>/edit/', views.denah_edit_kamar, name='denah_edit_kamar'),
    path('api/kamar/<int:pk>/delete/', views.denah_delete_kamar, name='denah_delete_kamar'),
]
