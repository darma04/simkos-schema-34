"""
PENYEWA URLS - Routing URL untuk modul Penyewa
"""
from django.urls import path
from . import views

app_name = 'penyewa'

urlpatterns = [
    path('', views.PenyewaListView.as_view(), name='list'),
    path('add/', views.PenyewaCreateView.as_view(), name='add'),
    path('<int:pk>/', views.PenyewaDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.PenyewaUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.PenyewaDeleteView.as_view(), name='delete'),
]
