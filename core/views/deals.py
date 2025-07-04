from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse
from ..models import Deal, Client, Contract
from ..forms import DealForm
import csv
from datetime import timedelta


def list_deals_view(request):
    # Получаем параметры фильтрации
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    start_date = request.GET.get('start', '')
    end_date = request.GET.get('end', '')

    # Базовый запрос
    deals = Deal.objects.select_related('client').all()

    # Применяем фильтры
    if query:
        deals = deals.filter(
            Q(title__icontains=query) |
            Q(client__name__icontains=query)
        ).distinct()

    if status:
        deals = deals.filter(status=status)

    if start_date:
        deals = deals.filter(created_at__date__gte=start_date)

    if end_date:
        deals = deals.filter(created_at__date__lte=end_date)

    # Контекст для шаблона
    context = {
        'deals': deals,
        'query': query,
        'status': status,
        'start': start_date,
        'end': end_date,
        'today': timezone.now().date()
    }

    # Обработка экспорта
    export_format = request.GET.get('export')
    if export_format == 'csv':
        return generate_csv_export(deals)
    elif export_format == 'xlsx':
        return generate_excel_export(deals)

    return render(request, 'core/deals/list.html', context)


def create_deal_view(request):
    if request.method == 'POST':
        form = DealForm(request.POST)
        if form.is_valid():
            deal = form.save()

            # Проверяем, не существует ли уже договор для этой сделки
            if not Contract.objects.filter(deal=deal).exists():
                Contract.objects.create(
                    client=deal.client,
                    deal=deal,
                    start_date=timezone.now().date(),
                    end_date=timezone.now().date() + timedelta(days=30),
                    price=0,
                    signed=False
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


def view_deal_view(request, pk):
    deal = get_object_or_404(
        Deal.objects.select_related('client').prefetch_related('contracts'),
        pk=pk
    )
    return render(request, 'core/deals/view.html', {'deal': deal})


def generate_csv_export(queryset):
    """Генерация экспорта в CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="deals_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Название', 'Клиент', 'Статус', 'Дата создания'])

    for deal in queryset:
        writer.writerow([
            deal.id,
            deal.title,
            deal.client.name,
            deal.get_status_display(),
            deal.created_at.strftime('%Y-%m-%d')
        ])

    return response


def generate_excel_export(queryset):
    """Генерация экспорта в Excel"""
    # Здесь должна быть реализация экспорта в Excel
    # Временно возвращаем CSV, пока не реализован Excel экспорт
    return generate_csv_export(queryset)