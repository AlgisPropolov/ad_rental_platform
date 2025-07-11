from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from ..models import Deal, Client, Contract
from core.forms.deal import DealForm
import csv
from datetime import timedelta


class DealBaseView:
    """Базовый класс для всех представлений сделок"""
    model = Deal
    context_object_name = 'deal'

    def get_success_url(self):
        return reverse_lazy('core:deal-list')


class DealListView(DealBaseView, ListView):
    template_name = 'core/deals/list.html'
    paginate_by = 20
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset().select_related('client')
        query = self.request.GET.get('q', '')
        status = self.request.GET.get('status', '')
        start_date = self.request.GET.get('start', '')
        end_date = self.request.GET.get('end', '')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(client__name__icontains=query)
            ).distinct()

        if status:
            queryset = queryset.filter(status=status)

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)

        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'query': self.request.GET.get('q', ''),
            'status': self.request.GET.get('status', ''),
            'start': self.request.GET.get('start', ''),
            'end': self.request.GET.get('end', ''),
            'today': timezone.now().date()
        })
        return context


class DealCreateView(DealBaseView, CreateView):
    form_class = DealForm
    template_name = 'core/deals/form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Сделка "{self.object.title}" создана')

        # Создаем пустой договор для новой сделки
        if not Contract.objects.filter(deal=self.object).exists():
            Contract.objects.create(
                client=self.object.client,
                deal=self.object,
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timedelta(days=30),
                total_amount=0,
                signed=False
            )
            messages.info(self.request, 'Автоматически создан пустой договор')

        return response


class DealUpdateView(DealBaseView, UpdateView):
    form_class = DealForm
    template_name = 'core/deals/form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Сделка "{self.object.title}" обновлена')
        return response


class DealDetailView(DealBaseView, DetailView):
    template_name = 'core/deals/detail.html'

    def get_queryset(self):
        return super().get_queryset().select_related('client').prefetch_related(
            Prefetch('contracts', queryset=Contract.objects.select_related('client'))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contracts'] = self.object.contracts.all()
        return context


class DealDeleteView(DealBaseView, DeleteView):
    template_name = 'core/deals/confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        deal = self.get_object()

        if deal.contracts.exists():
            messages.error(
                request,
                'Нельзя удалить сделку с привязанными договорами'
            )
            return redirect('core:deal-detail', pk=deal.pk)

        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Сделка "{deal.title}" удалена')
        return response


def generate_csv_export(queryset):
    """Генерация экспорта сделок в CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="deals_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Название', 'Клиент', 'Статус', 'Дата создания', 'Кол-во договоров'])

    for deal in queryset.select_related('client').annotate(contracts_count=Count('contracts')):
        writer.writerow([
            deal.id,
            deal.title,
            deal.client.name,
            deal.get_status_display(),
            deal.created_at.strftime('%Y-%m-%d'),
            deal.contracts_count
        ])

    return response


def generate_excel_export(queryset):
    """Заглушка для Excel экспорта (пока используем CSV)"""
    return generate_csv_export(queryset)