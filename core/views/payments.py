from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from ..models import Payment
from core.forms.payment import PaymentForm  # Убедитесь, что у вас есть этот файл форм

class PaymentListView(ListView):
    model = Payment
    template_name = 'core/payments/list.html'
    context_object_name = 'payments'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related('contract', 'contract__client')

class PaymentCreateView(CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'core/payments/create.html'
    success_url = reverse_lazy('payment-list')

    def form_valid(self, form):
        # Дополнительная логика при создании платежа
        return super().form_valid(form)

class PaymentDetailView(DetailView):
    model = Payment
    template_name = 'core/payments/detail.html'
    context_object_name = 'payment'

    def get_queryset(self):
        return super().get_queryset().select_related('contract', 'contract__client')