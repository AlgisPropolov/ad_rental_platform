from django.shortcuts import render
from core.models import AvailabilitySlot

def availability_view(request):
    slots = AvailabilitySlot.objects.select_related('asset').order_by('start_date')
    return render(request, 'core/availability.html', {'slots': slots})
