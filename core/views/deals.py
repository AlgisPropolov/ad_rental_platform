from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from ..models import Deal, Client, Contract
from core.forms.deal import DealForm
import csv
from datetime import timedelta


class DealListView(ListView):
    model = Deal
    template_name = 'core/deals/list.html'
    context_object_name = 'deals'
    paginate_by = 20

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


class DealCreateView(CreateView):
    model = Deal
    form_class = DealForm
    template_name = 'core/deals/create.html'
    success_url = '/deals/'

    def form_valid(self, form):
        response = super().form_valid(form)
        if not Contract.objects.filter(deal=self.object).exists():
            Contract.objects.create(
                client=self.object.client,
                deal=self.object,
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timedelta(days=30),
                price=0,
                signed=False
            )
        return response


class DealUpdateView(UpdateView):
    model = Deal
    form_class = DealForm
    template_name = 'core/deals/edit.html'
    success_url = '/deals/'


class DealDeleteView(DeleteView):
    model = Deal
    template_name = 'core/deals/delete.html'
    success_url = '/deals/'


class DealDetailView(DetailView):
    model = Deal
    template_name = 'core/deals/view.html'
    context_object_name = 'deal'

    def get_queryset(self):
        return super().get_queryset().select_related('client').prefetch_related('contracts')


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
    # Временно возвращаем CSV, пока не реализован Excel экспорт
    return generate_csv_export(queryset)