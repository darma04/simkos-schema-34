"""
PENYEWA FORMS - Form untuk Data Penyewa
"""
from django import forms
from apps.penyewa.models import Penyewa


class PenyewaForm(forms.ModelForm):
    class Meta:
        model = Penyewa
        fields = [
            'nama', 'nik', 'jenis_kelamin', 'telepon', 'email',
            'alamat_asal', 'pekerjaan', 'foto_ktp', 'foto',
            'kontak_darurat_nama', 'kontak_darurat_telepon', 'kontak_darurat_hubungan',
            'status', 'catatan'
        ]
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'nik': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '16', 'placeholder': '16 digit NIK KTP'}),
            'jenis_kelamin': forms.Select(attrs={'class': 'form-select'}),
            'telepon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '08xxxxxxxxxx'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'alamat_asal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pekerjaan': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_ktp': forms.FileInput(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'kontak_darurat_nama': forms.TextInput(attrs={'class': 'form-control'}),
            'kontak_darurat_telepon': forms.TextInput(attrs={'class': 'form-control'}),
            'kontak_darurat_hubungan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Orang Tua / Saudara / Teman'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'catatan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
