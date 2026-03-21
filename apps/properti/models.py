"""
==========================================================================
 PROPERTI MODELS - Model Properti, Tipe Kamar, dan Kamar
==========================================================================
 File ini berisi 3 model untuk manajemen properti kost/kontrakan:

 1. Properti  - Data properti (nama, alamat, tipe: kost/kontrakan)
 2. TipeKamar - Tipe kamar (AC, Non-AC, VIP) dengan harga dan fasilitas
 3. Kamar     - Detail setiap kamar (nomor, lantai, status hunian)
==========================================================================
"""

from django.db import models
from django.contrib.auth.models import User


class Properti(models.Model):
    """Model untuk data PROPERTI (kost atau kontrakan)."""

    TIPE_CHOICES = [
        ('kost', 'Kost'),
        ('kontrakan', 'Kontrakan'),
        ('apartemen', 'Apartemen'),
        ('rumah', 'Rumah Sewa'),
    ]

    nama = models.CharField(max_length=200, verbose_name="Nama Properti")
    tipe = models.CharField(max_length=20, choices=TIPE_CHOICES, default='kost', verbose_name="Tipe Properti")
    alamat = models.TextField(verbose_name="Alamat Lengkap")
    kota = models.CharField(max_length=100, blank=True, null=True, verbose_name="Kota/Kabupaten")
    deskripsi = models.TextField(blank=True, null=True, verbose_name="Deskripsi")
    foto = models.ImageField(upload_to='properti/', blank=True, null=True, verbose_name="Foto Properti")
    pemilik = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nama Pemilik")
    telepon = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telepon")
    aktif = models.BooleanField(default=True, verbose_name="Aktif")

    dibuat_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='properti_dibuat')
    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diupdate_pada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Properti"
        verbose_name_plural = "Properti"
        ordering = ['nama']

    def __str__(self):
        return f"{self.nama} ({self.get_tipe_display()})"

    @property
    def total_kamar(self):
        return self.kamar_set.count()

    @property
    def kamar_tersedia(self):
        return self.kamar_set.filter(status='tersedia').count()

    @property
    def kamar_terisi(self):
        return self.kamar_set.filter(status='terisi').count()


class TipeKamar(models.Model):
    """Model untuk TIPE KAMAR (Standard, AC, VIP, Studio, dll)."""

    nama = models.CharField(max_length=100, verbose_name="Nama Tipe")
    harga_bulanan = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Harga per Bulan (Rp)")
    fasilitas = models.TextField(blank=True, null=True, verbose_name="Fasilitas", help_text="Pisahkan dengan koma. Contoh: AC, WiFi, Kamar Mandi Dalam")
    deskripsi = models.TextField(blank=True, null=True, verbose_name="Deskripsi")
    aktif = models.BooleanField(default=True, verbose_name="Aktif")

    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diupdate_pada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tipe Kamar"
        verbose_name_plural = "Tipe Kamar"
        ordering = ['nama']

    def __str__(self):
        return f"{self.nama} - Rp {self.harga_bulanan:,.0f}/bulan"


class Kamar(models.Model):
    """Model untuk data KAMAR di sebuah properti."""

    STATUS_CHOICES = [
        ('tersedia', 'Tersedia'),
        ('terisi', 'Terisi'),
        ('maintenance', 'Perbaikan'),
    ]

    properti = models.ForeignKey(Properti, on_delete=models.CASCADE, verbose_name="Properti")
    tipe_kamar = models.ForeignKey(TipeKamar, on_delete=models.SET_NULL, null=True, verbose_name="Tipe Kamar")
    nomor_kamar = models.CharField(max_length=20, verbose_name="Nomor Kamar")
    lantai = models.PositiveIntegerField(default=1, verbose_name="Lantai")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='tersedia', verbose_name="Status")
    fasilitas_tambahan = models.TextField(blank=True, null=True, verbose_name="Fasilitas Tambahan")
    catatan = models.TextField(blank=True, null=True, verbose_name="Catatan")

    # Posisi untuk denah interaktif
    pos_x = models.IntegerField(default=0, verbose_name="Posisi X (denah)")
    pos_y = models.IntegerField(default=0, verbose_name="Posisi Y (denah)")
    width = models.IntegerField(default=100, verbose_name="Lebar (denah)")
    height = models.IntegerField(default=80, verbose_name="Tinggi (denah)")

    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diupdate_pada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kamar"
        verbose_name_plural = "Kamar"
        ordering = ['properti', 'nomor_kamar']
        unique_together = ['properti', 'nomor_kamar']

    def __str__(self):
        return f"{self.properti.nama} - Kamar {self.nomor_kamar}"

    @property
    def harga(self):
        """Harga bulanan dari tipe kamar."""
        if self.tipe_kamar:
            return self.tipe_kamar.harga_bulanan
        return 0
