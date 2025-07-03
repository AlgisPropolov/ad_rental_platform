# ✅ core/views/availability.py

from django.shortcuts import render
from core.models import AvailabilitySlot
from django import forms

class AvailabilityFilterForm(forms.Form):
    date = forms.DateField(
        required=False,
        label='На дату',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    asset_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Все типы'), ('bus', 'Автобус'), ('stop', 'Остановка'), ('screen', 'Медиаэкран')],
        label='Тип объекта'
    )

def availability_view(request):
    form = AvailabilityFilterForm(request.GET or None)
    slots = AvailabilitySlot.objects.select_related('asset').all()

    if form.is_valid():
        date = form.cleaned_data.get('date')
        asset_type = form.cleaned_data.get('asset_type')

        if date:
            slots = slots.filter(start_date__lte=date, end_date__gte=date)
        if asset_type:
            slots = slots.filter(asset__asset_type=asset_type)

    grouped_slots = {}
    for slot in slots.order_by('start_date'):
        asset_id = slot.asset.id
        if asset_id not in grouped_slots:
            grouped_slots[asset_id] = {
                'asset': slot.asset,
                'slots': []
            }
        grouped_slots[asset_id]['slots'].append(slot)

    return render(request, 'core/availability/index.html', {
        'grouped_slots': grouped_slots,
        'form': form,
    })
