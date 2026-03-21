"""
==========================================================================
 ACTIVITY LOG APPS - Konfigurasi Aplikasi Log Aktivitas
==========================================================================
 File apps.py wajib ada di setiap Django app. Berisi konfigurasi dasar:
 - name: Path lengkap app (harus sesuai dengan INSTALLED_APPS di settings.py)
 - verbose_name: Nama tampilan di Django Admin
 - ready(): Dipanggil SEKALI saat Django startup — tempat mendaftarkan signals

 PENTING: Method ready() adalah tempat yang TEPAT untuk:
 - Mendaftarkan signal handlers
 - Import module yang memiliki @receiver decorator
 - Konfigurasi awal yang perlu dijalankan saat startup
==========================================================================
"""
from django.apps import AppConfig


class ActivityLogConfig(AppConfig):
    """Konfigurasi aplikasi Activity Log — pencatatan aktivitas user."""
    default_auto_field = 'django.db.models.BigAutoField'  # Tipe ID default = BigAutoField (int 64-bit)
    name = 'apps.activity_log'     # Path lengkap app (harus cocok dengan folder structure)
    verbose_name = 'Activity Log'  # Nama tampilan di Django Admin

    def ready(self):
        """
        Dipanggil otomatis SEKALI saat Django startup (runserver, migrate, dll).
        Di sini kita mendaftarkan signal handlers untuk auto-logging
        ke SEMUA model di aplikasi (kecuali yang di-exclude).
        """
        from .signals import register_signals
        register_signals()
