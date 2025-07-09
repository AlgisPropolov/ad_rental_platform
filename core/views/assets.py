from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
    View
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from core.models import Asset
from core.forms import AssetForm  # Рекомендуется использовать явную форму

class AssetListView(ListView):
    """Список всех активов с пагинацией"""
    model = Asset
    template_name = 'core/assets/list.html'
    context_object_name = 'assets'
    ordering = ['-created_at']
    paginate_by = 20

    def get_queryset(self):
        """Дополнительная фильтрация активов"""
        queryset = super().get_queryset()
        # Пример фильтрации по типу актива
        asset_type = self.request.GET.get('asset_type')
        if asset_type:
            queryset = queryset.filter(asset_type=asset_type)
        return queryset

class AssetCreateView(CreateView):
    """Создание нового актива"""
    model = Asset
    form_class = AssetForm  # Используем явную форму вместо fields = '__all__'
    template_name = 'core/assets/create.html'
    success_url = reverse_lazy('core:asset-list')

    def form_valid(self, form):
        """Добавление сообщения об успешном создании"""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Актив "{self.object.name}" успешно создан'
        )
        return response

class AssetDetailView(DetailView):
    """Детальная информация об активе"""
    model = Asset
    template_name = 'core/assets/detail.html'
    context_object_name = 'asset'

    def get_context_data(self, **kwargs):
        """Добавление дополнительного контекста"""
        context = super().get_context_data(**kwargs)
        context['availability_slots'] = self.object.availability_slots.all()
        return context

class AssetUpdateView(UpdateView):
    """Редактирование актива"""
    model = Asset
    form_class = AssetForm
    template_name = 'core/assets/update.html'
    success_url = reverse_lazy('core:asset-list')

    def form_valid(self, form):
        """Добавление сообщения об успешном обновлении"""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Актив "{self.object.name}" успешно обновлен'
        )
        return response

class AssetDeleteView(DeleteView):
    """Удаление актива"""
    model = Asset
    template_name = 'core/assets/delete.html'
    success_url = reverse_lazy('core:asset-list')
    context_object_name = 'asset'

    def delete(self, request, *args, **kwargs):
        """Добавление сообщения об успешном удалении"""
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Актив успешно удален')
        return response

class AssetSlotsView(View):
    """API для получения слотов доступности актива"""
    def get(self, request, *args, **kwargs):
        asset = get_object_or_404(Asset, pk=kwargs['asset_id'])
        slots = asset.availability_slots.values(
            'id',
            'start_date',
            'end_date',
            'is_available'
        )
        return JsonResponse(list(slots), safe=False)