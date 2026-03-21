"""
==========================================================================
 SEWA APPS - Konfigurasi aplikasi Django untuk modul Sewa
==========================================================================
"""
from django.apps import AppConfig


class SewaConfig(AppConfig):
    """Konfigurasi aplikasi Sewa (Kontrak, Tagihan, Pembayaran)."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sewa'
    verbose_name = 'Sewa'
