"""
==========================================================================
 PENYEWA APPS - Konfigurasi aplikasi Django untuk modul Penyewa
==========================================================================
"""
from django.apps import AppConfig


class PenyewaConfig(AppConfig):
    """Konfigurasi aplikasi Penyewa."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.penyewa'
    verbose_name = 'Penyewa'
