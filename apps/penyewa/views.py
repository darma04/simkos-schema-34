"""
==========================================================================
 PENYEWA VIEWS - Views CRUD untuk manajemen penyewa
==========================================================================
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from apps.penyewa.models import Penyewa
from apps.penyewa.forms import PenyewaForm
from web_project import TemplateLayout
from django.db import transaction


class PenyewaListView(ListView):
    paginate_by = 50
    """Daftar semua penyewa."""
    model = Penyewa
    template_name = 'penyewa/penyewa_list.html'
    context_object_name = 'penyewa_list'

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        status = self.request.GET.get('status', '').strip()
        if q:
            qs = qs.filter(nama__icontains=q)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        qs = self.get_queryset()
        context['total_penyewa'] = qs.count()
        context['penyewa_aktif'] = qs.filter(status='aktif').count()
        return context



class PenyewaDetailView(DetailView):
    """Detail penyewa lengkap dengan riwayat kontrak."""
    model = Penyewa
    template_name = 'penyewa/penyewa_detail.html'
    context_object_name = 'penyewa'

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        from apps.sewa.models import KontrakSewa
        context['kontrak_list'] = KontrakSewa.objects.filter(
            penyewa=self.object
        ).select_related('kamar', 'kamar__properti').order_by('-tanggal_masuk')
        return context


class PenyewaCreateView(CreateView):
    model = Penyewa
    form_class = PenyewaForm
    template_name = 'penyewa/penyewa_form.html'
    success_url = reverse_lazy('penyewa:list')

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['title'] = 'Tambah Penyewa'
        context['is_edit'] = False
        return context

    def form_valid(self, form):
        """Simpan data penyewa baru."""
        messages.success(self.request, 'Penyewa berhasil ditambahkan')
        return super().form_valid(form)


class PenyewaUpdateView(UpdateView):
    model = Penyewa
    form_class = PenyewaForm
    template_name = 'penyewa/penyewa_form.html'
    success_url = reverse_lazy('penyewa:list')

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['title'] = 'Edit Penyewa'
        context['is_edit'] = True
        return context

    def form_valid(self, form):
        """Update data penyewa."""
        messages.success(self.request, 'Data penyewa berhasil diperbarui')
        return super().form_valid(form)


class PenyewaDeleteView(DeleteView):
    model = Penyewa
    success_url = reverse_lazy('penyewa:list')

    def delete(self, request, *args, **kwargs):
        from django.db.models import ProtectedError
        self.object = self.get_object()
        try:
            nama = self.object.nama
            self.object.delete()
            return JsonResponse({'success': True, 'message': f'Penyewa {nama} berhasil dihapus'})
        except ProtectedError:
            return JsonResponse({'success': False, 'message': f'Tidak dapat menghapus penyewa "{self.object.nama}" karena masih memiliki kontrak sewa aktif. Silakan hapus atau akhiri kontrak terkait terlebih dahulu.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Terjadi kesalahan saat menghapus data. Silakan coba lagi.'})

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)
