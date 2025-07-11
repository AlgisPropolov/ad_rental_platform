from django import forms
from django.shortcuts import render
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import F
from django.views import View  # Добавлен этот импорт
from ..models import Asset, AvailabilitySlot


def get_asset_types():
    """Возвращает варианты типов активов для фильтра"""
    return [('', 'Все типы')] + Asset.AssetType.choices


class AvailabilityFilterForm(forms.Form):
    """Форма фильтрации слотов доступности"""
    date = forms.DateField(
        required=False,
        label='На дату',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'max': timezone.now().date().isoformat()
        }),
        initial=timezone.now().date
    )
    asset_type = forms.ChoiceField(
        required=False,
        choices=get_asset_types,
        label='Тип объекта',
        widget=forms.Select(attrs={'class': 'form-control'})
    )


def group_slots_by_asset(slots):
    """Группирует слоты по активам для удобного отображения"""
    grouped = {}
    for slot in slots.select_related('asset'):
        if slot.asset_id not in grouped:
            grouped[slot.asset_id] = {
                'asset': slot.asset,
                'slots': []
            }
        grouped[slot.asset_id]['slots'].append({
            'id': slot.id,
            'start_date': slot.start_date,
            'end_date': slot.end_date,
            'is_available': slot.is_available,
            'reserved_by': slot.reserved_by.name if slot.reserved_by else None
        })
    return grouped


class AvailabilityView(View):
    """CBV для отображения доступности активов"""
    template_name = 'core/availability/index.html'
    paginate_by = 20

    def get(self, request):
        form = AvailabilityFilterForm(request.GET or None)
        today = timezone.now().date()
        slots = AvailabilitySlot.objects.order_by('asset__name', 'start_date')

        if form.is_valid():
            date = form.cleaned_data.get('date') or today
            asset_type = form.cleaned_data.get('asset_type')

            slots = slots.filter(
                start_date__lte=date,
                end_date__gte=date
            )

            if asset_type:
                slots = slots.filter(asset__asset_type=asset_type)

        grouped_slots = group_slots_by_asset(slots)
        paginator = Paginator(list(grouped_slots.items()), self.paginate_by)
        page_obj = paginator.get_page(request.GET.get('page'))

        context = {
            'form': form,
            'grouped_slots': dict(page_obj.object_list),
            'page_obj': page_obj,
            'current_date': today,
            'page_title': 'Доступность рекламных поверхностей'
        }
        return render(request, self.template_name, context)


def availability_view(request):
    """Функциональное представление для обратной совместимости"""
    return AvailabilityView.as_view()(request)