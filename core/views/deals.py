# ✅ core/views/deals.py
from django.shortcuts import render, redirect, get_object_or_404
from core.models import Deal, Client, Asset, Contract
from core.forms import DealForm
from django.db.models import Q
import datetime

def list_deals_view(request):
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    start = request.GET.get('start', '')
    end = request.GET.get('end', '')

    deals = Deal.objects.select_related('client', 'asset').all()

    if query:
        deals = deals.filter(Q(client__name__icontains=query) | Q(asset__name__icontains=query))
    if status:
        deals = deals.filter(status=status)
    if start:
        deals = deals.filter(start_date__gte=start)
    if end:
        deals = deals.filter(end_date__lte=end)

    return render(request, 'core/deals/list.html', {
        'deals': deals,
        'query': query,
        'status': status,
        'start': start,
        'end': end,
    })

def create_deal_view(request):
    if request.method == 'POST':
        form = DealForm(request.POST)
        if form.is_valid():
            deal = form.save()

            # 📝 Автосоздание договора после создания сделки
            Contract.objects.create(
                client=deal.client,
                deal=deal,
                start_date=deal.start_date,
                end_date=deal.end_date,
                total_amount=deal.amount,
                status='draft'
            )

            return redirect('list_deals')
    else:
        form = DealForm()
    return render(request, 'core/deals/create.html', {'form': form})

def edit_deal_view(request, pk):
    deal = get_object_or_404(Deal, pk=pk)
    if request.method == 'POST':
        form = DealForm(request.POST, instance=deal)
        if form.is_valid():
            form.save()
            return redirect('list_deals')
    else:
        form = DealForm(instance=deal)
    return render(request, 'core/deals/edit.html', {'form': form, 'deal': deal})

def delete_deal_view(request, pk):
    deal = get_object_or_404(Deal, pk=pk)
    if request.method == 'POST':
        deal.delete()
        return redirect('list_deals')
    return render(request, 'core/deals/delete.html', {'deal': deal})
