"""
==========================================================================
 PERMISSION MANAGEMENT APPS - Konfigurasi Aplikasi Manajemen Permission
==========================================================================
 Modul untuk mengelola permission (akses kontrol) dan roles.
 Tidak memiliki models sendiri — menggunakan RolePermission dari core.
 Menyediakan views untuk CRUD permission dan CRUD roles.

 Terhubung dengan:
 - core/models.py → RolePermission (model utama)
 - permission_management/views.py → CRUD permission
 - permission_management/views_roles.py → CRUD roles
==========================================================================
"""
from django.apps import AppConfig


class PermissionManagementConfig(AppConfig):
    """Konfigurasi aplikasi Permission Management — kelola hak akses role."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.permission_management'
    verbose_name = 'Permission Management'
