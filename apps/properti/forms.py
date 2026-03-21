"""
PROPERTI FORMS - Form untuk Properti, Tipe Kamar, dan Kamar
"""
from django import forms
from apps.properti.models import Properti, TipeKamar, Kamar


class PropertiForm(forms.ModelForm):
    class Meta:
        model = Properti
        fields = ['nama', 'tipe', 'alamat', 'kota', 'deskripsi', 'foto', 'pemilik', 'telepon', 'aktif']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'tipe': forms.Select(attrs={'class': 'form-select'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'kota': forms.TextInput(attrs={'class': 'form-control'}),
            'deskripsi': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'pemilik': forms.TextInput(attrs={'class': 'form-control'}),
            'telepon': forms.TextInput(attrs={'class': 'form-control'}),
            'aktif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TipeKamarForm(forms.ModelForm):
    class Meta:
        model = TipeKamar
        fields = ['nama', 'harga_bulanan', 'fasilitas', 'deskripsi', 'aktif']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'harga_bulanan': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'fasilitas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'AC, WiFi, Kamar Mandi Dalam, Lemari'}),
            'deskripsi': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'aktif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class KamarForm(forms.ModelForm):
    class Meta:
        model = Kamar
        fields = ['properti', 'tipe_kamar', 'nomor_kamar', 'lantai', 'status', 'fasilitas_tambahan', 'catatan']
        widgets = {
            'properti': forms.Select(attrs={'class': 'form-select'}),
            'tipe_kamar': forms.Select(attrs={'class': 'form-select'}),
            'nomor_kamar': forms.TextInput(attrs={'class': 'form-control'}),
            'lantai': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'fasilitas_tambahan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'catatan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['properti'].queryset = Properti.objects.filter(aktif=True)
        self.fields['properti'].empty_label = 'Pilih Properti'
        self.fields['tipe_kamar'].queryset = TipeKamar.objects.filter(aktif=True)
        self.fields['tipe_kamar'].empty_label = 'Pilih Tipe Kamar'
