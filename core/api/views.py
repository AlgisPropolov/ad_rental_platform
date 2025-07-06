from django.http import JsonResponse
from core.models import AvailabilitySlot


def asset_slots(request, asset_id):
    slots = AvailabilitySlot.objects.filter(
        asset_id=asset_id,
        is_available=True
    ).values('id', 'start_date', 'end_date')

    return JsonResponse({
        'slots': list(slots)
    })