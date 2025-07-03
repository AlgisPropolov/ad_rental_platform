# ✅ core/forms/deals.py
from django import forms
from django.utils import timezone
from core.models import Deal
from django.apps import apps

class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = ['title', 'client', 'assets', 'status']

    def save(self, commit=True):
        deal = super().save(commit=commit)

        # ✅ Получаем модель Contract без прямого импорта
        Contract = apps.get_model('core', 'Contract')

        # 🧠 Автоматическое создание договора
        if not Contract.objects.filter(client=deal.client, asset__in=deal.assets.all()).exists():
            for asset in deal.assets.all():
                Contract.objects.create(
                    client=deal.client,
                    asset=asset,
                    start_date=timezone.now().date(),
                    end_date=timezone.now().date() + timezone.timedelta(days=30),
                    amount=10000.00,  # можно сделать вычисляемой
                    signed=False
                )

        return deal
