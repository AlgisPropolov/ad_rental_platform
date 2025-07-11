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
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Prefetch, Q, F, Count
from django.utils import timezone
from core.models import Asset, AvailabilitySlot, Contract
from core.forms import AssetForm


class AssetBaseView:
    """Базовый класс для всех представлений активов"""
    model = Asset
    context_object_name = 'asset'

    def get_success_url(self):
        return reverse_lazy('core:asset-list')


class AssetListView(AssetBaseView, ListView):
    """Список активов с расширенной фильтрацией"""
    template_name = 'core/assets/list.html'
    paginate_by = 20
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'zone'
        ).prefetch_related(
            'tags'
        ).annotate(
            contracts_count=Count('contracts', distinct=True)  # Исправлено: заменено annotate_contracts_count()
        )

        # Фильтрация по параметрам
        filters = {
            'asset_type': self.request.GET.get('asset_type'),
            'zone_id': self.request.GET.get('zone'),
            'is_active': self.request.GET.get('is_active'),
            'search': self.request.GET.get('search')
        }

        if filters['asset_type']:
            queryset = queryset.filter(asset_type=filters['asset_type'])

        if filters['zone_id']:
            queryset = queryset.filter(zone_id=filters['zone_id'])

        if filters['is_active'] in ['true', 'false']:
            queryset = queryset.filter(is_active=(filters['is_active'] == 'true'))

        if filters['search']:
            queryset = queryset.filter(
                Q(name__icontains=filters['search']) |
                Q(location__icontains=filters['search'])
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_assets'] = self.get_queryset().count()
        return context


class AssetCreateView(AssetBaseView, CreateView):
    """Создание нового актива с обработкой тегов"""
    form_class = AssetForm
    template_name = 'core/assets/form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Актив "{self.object.name}" успешно создан (ID: {self.object.id})'
        )
        return response


class AssetDetailView(AssetBaseView, DetailView):
    """Детальная информация об активе со связанными данными"""
    template_name = 'core/assets/detail.html'

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            Prefetch('availability_slots',
                    queryset=AvailabilitySlot.objects.order_by('start_date')),
            Prefetch('contracts',
                    queryset=Contract.objects.select_related('client')
                    .only('id', 'number', 'client__name', 'start_date', 'end_date'))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asset = self.object
        context['current_contract'] = asset.contracts.filter(
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).first()
        return context


class AssetUpdateView(AssetBaseView, UpdateView):
    """Редактирование актива с обработкой тегов"""
    form_class = AssetForm
    template_name = 'core/assets/form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Актив "{self.object.name}" успешно обновлен'
        )
        return response


class AssetDeleteView(AssetBaseView, DeleteView):
    """Удаление актива с проверкой зависимостей"""
    template_name = 'core/assets/confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        asset = self.get_object()

        if asset.contracts.exists():
            messages.error(
                request,
                'Нельзя удалить актив с привязанными договорами'
            )
            return redirect('core:asset-detail', pk=asset.pk)

        response = super().delete(request, *args, **kwargs)
        messages.success(
            request,
            f'Актив "{asset.name}" успешно удален'
        )
        return response


class AssetSlotsView(View):
    """API для работы со слотами доступности актива"""
    def get(self, request, asset_id):
        asset = get_object_or_404(
            Asset.objects.only('id'),
            pk=asset_id
        )

        date_from = request.GET.get('from')
        date_to = request.GET.get('to')

        slots = asset.availability_slots.all()

        if date_from:
            slots = slots.filter(end_date__gte=date_from)
        if date_to:
            slots = slots.filter(start_date__lte=date_to)

        data = slots.annotate(
            reserved_by_name=F('reserved_by__name')
        ).values(
            'id',
            'start_date',
            'end_date',
            'is_available',
            'reserved_by_name'
        ).order_by('start_date')

        return JsonResponse(list(data), safe=False)