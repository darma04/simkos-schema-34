"""
==========================================================================
 PENYEWA MODELS - Model Data Penyewa Kost/Kontrakan
==========================================================================
"""

from django.db import models
from django.contrib.auth.models import User


class Penyewa(models.Model):
    """Model untuk data PENYEWA kost/kontrakan."""

    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('nonaktif', 'Nonaktif'),
        ('blacklist', 'Blacklist'),
    ]

    JENIS_KELAMIN_CHOICES = [
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    ]

    nama = models.CharField(max_length=200, verbose_name="Nama Lengkap")
    nik = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="NIK (KTP)")
    jenis_kelamin = models.CharField(max_length=1, choices=JENIS_KELAMIN_CHOICES, blank=True, null=True, verbose_name="Jenis Kelamin")
    telepon = models.CharField(max_length=20, verbose_name="No. Telepon")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    alamat_asal = models.TextField(blank=True, null=True, verbose_name="Alamat Asal")
    pekerjaan = models.CharField(max_length=100, blank=True, null=True, verbose_name="Pekerjaan")
    foto_ktp = models.ImageField(upload_to='penyewa/ktp/', blank=True, null=True, verbose_name="Foto KTP")
    foto = models.ImageField(upload_to='penyewa/foto/', blank=True, null=True, verbose_name="Foto Penyewa")

    kontak_darurat_nama = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nama Kontak Darurat")
    kontak_darurat_telepon = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telepon Kontak Darurat")
    kontak_darurat_hubungan = models.CharField(max_length=50, blank=True, null=True, verbose_name="Hubungan")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif', verbose_name="Status")
    catatan = models.TextField(blank=True, null=True, verbose_name="Catatan")

    dibuat_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='penyewa_dibuat')
    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diupdate_pada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Penyewa"
        verbose_name_plural = "Penyewa"
        ordering = ['nama']

    def __str__(self):
        return self.nama
