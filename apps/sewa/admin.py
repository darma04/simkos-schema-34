from django.contrib import admin
from apps.sewa.models import KontrakSewa, TagihanSewa, PembayaranSewa

admin.site.register(KontrakSewa)
admin.site.register(TagihanSewa)
admin.site.register(PembayaranSewa)
