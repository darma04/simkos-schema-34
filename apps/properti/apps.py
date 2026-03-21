"""
==========================================================================
 PROPERTI APPS - Konfigurasi aplikasi Django untuk modul Properti
==========================================================================
"""
from django.apps import AppConfig


class PropertiConfig(AppConfig):
    """Konfigurasi aplikasi Properti (Kost & Kontrakan)."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.properti'
    verbose_name = 'Properti'
