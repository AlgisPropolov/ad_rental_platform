from django import forms
from django.shortcuts import render
from django.utils import timezone
from django.core.paginator import Paginator
from ..models import Asset, AvailabilitySlot


def get_asset_types():
    return [('', 'Все типы')] + Asset.AssetType.choices


class AvailabilityFilterForm(forms.Form):
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
    for slot in slots:
        if slot.asset_id not in grouped:
            grouped[slot.asset_id] = {
                'asset': slot.asset,
                'slots': []
            }
        grouped[slot.asset_id]['slots'].append(slot)
    return grouped


def availability_view(request):
    form = AvailabilityFilterForm(request.GET or None)
    today = timezone.now().date()
    slots = AvailabilitySlot.objects.select_related('asset').order_by('asset__name', 'start_date')

    if form.is_valid():
        date = form.cleaned_data.get('date') or today
        asset_type = form.cleaned_data.get('asset_type')

        slots = slots.filter(
            start_date__lte=date,
            end_date__gte=date
        )

        if asset_type:
            slots = slots.filter(asset__asset_type=asset_type)

    # Группировка и пагинация
    grouped_slots = group_slots_by_asset(slots)
    paginator = Paginator(list(grouped_slots.items()), 20)  # 20 элементов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'grouped_slots': dict(page_obj.object_list),
        'page_obj': page_obj,
        'current_date': today,
        'page_title': 'Доступность рекламных поверхностей'
    }

    return render(request, 'core/availability/index.html', context)