from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.apps import apps
from core.models import Deal, Client, Asset


class DealForm(forms.ModelForm):
    description = forms.CharField(
        label=_('Описание сделки'),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Детали сделки, особые условия...')
        }),
        required=False
    )

    assets = forms.ModelMultipleChoiceField(
        label=_('Рекламные активы'),
        queryset=Asset.objects.none(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select select2-multiple',
            'data-placeholder': _('Выберите активы')
        }),
        required=False
    )

    def __init__(self, *args, **kwargs):
        """Инициализация формы с оптимизацией запросов"""
        super().__init__(*args, **kwargs)
        self.fields['assets'].queryset = Asset.objects.available().select_related('zone')

        # Оптимизация queryset'ов
        self.fields['client'].queryset = Client.objects.all().only('id', 'name')
        self.fields['manager'].queryset = self.fields['manager'].queryset.only('id', 'username')

        # Настройка виджетов
        self.fields['expected_amount'].widget.attrs.update({
            'step': '500',
            'min': '1000'
        })
        self.fields['probability'].widget.attrs.update({
            'min': '0',
            'max': '100'
        })
        self.fields['closed_at'].widget.attrs.update({
            'class': 'datepicker'
        })

    class Meta:
        model = Deal
        fields = ['title', 'client', 'manager', 'status', 'expected_amount',
                  'probability', 'closed_at']
        labels = {
            'title': _('Название сделки'),
            'client': _('Клиент'),
            'manager': _('Менеджер'),
            'status': _('Статус'),
            'expected_amount': _('Ожидаемая сумма (руб)'),
            'probability': _('Вероятность успеха (%)'),
            'closed_at': _('Дата закрытия'),
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Например: Рекламная кампания Pepsi 2024')
            }),
            'client': forms.Select(attrs={
                'class': 'form-select select2',
                'data-placeholder': _('Выберите клиента')
            }),
            'manager': forms.Select(attrs={
                'class': 'form-select select2',
                'data-placeholder': _('Выберите менеджера')
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'expected_amount': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'probability': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'closed_at': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        help_texts = {
            'probability': _('0-100%, где 100% - гарантированная сделка'),
            'assets': _('Удерживайте Ctrl для выбора нескольких активов'),
        }

    def clean_expected_amount(self):
        """Валидация ожидаемой суммы"""
        amount = self.cleaned_data.get('expected_amount')
        if amount and amount < 1000:
            raise ValidationError(
                _("Минимальная сумма сделки - 1 000 рублей")
            )
        return amount

    def clean_probability(self):
        """Валидация вероятности"""
        probability = self.cleaned_data.get('probability')
        if probability and (probability < 0 or probability > 100):
            raise ValidationError(
                _("Вероятность должна быть между 0 и 100%")
            )
        return probability

    def clean_closed_at(self):
        """Валидация даты закрытия"""
        closed_at = self.cleaned_data.get('closed_at')
        if closed_at and closed_at < timezone.now().date():
            raise ValidationError(
                _("Дата закрытия не может быть в прошлом")
            )
        return closed_at

    def clean(self):
        """Комплексная валидация формы"""
        cleaned_data = super().clean()

        # Проверка соответствия статуса и вероятности
        status = cleaned_data.get('status')
        probability = cleaned_data.get('probability')

        if status == 'won' and probability != 100:
            self.add_error(
                'probability',
                _("Для успешной сделки вероятность должна быть 100%")
            )

        if status == 'lost' and probability != 0:
            self.add_error(
                'probability',
                _("Для проваленной сделки вероятность должна быть 0%")
            )

        return cleaned_data

    def save(self, commit=True):
        """Сохранение сделки с дополнительной логикой"""
        deal = super().save(commit=False)

        # Автоматическое закрытие сделки при статусе won/lost
        if deal.status in ['won', 'lost'] and not deal.closed_at:
            deal.closed_at = timezone.now()

        if commit:
            deal.save()
            self.save_m2m()  # Сохраняем ManyToMany связи

            # Создание связанных договоров
            if not self.instance.pk:  # Только для новых сделок
                self._create_contracts(deal)

        return deal

    def _create_contracts(self, deal):
        """Создание договоров для активов"""
        Contract = apps.get_model('core', 'Contract')
        assets = self.cleaned_data.get('assets', [])

        for asset in assets:
            Contract.objects.create(
                client=deal.client,
                deal=deal,
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timezone.timedelta(days=30),
                total_amount=self._calculate_asset_amount(asset),
                payment_type='partial',
                signed=False
            )

    def _calculate_asset_amount(self, asset):
        """Расчет суммы для актива"""
        base_amount = self.cleaned_data.get('expected_amount', 0)
        assets_count = len(self.cleaned_data.get('assets', []))
        return round(base_amount / max(1, assets_count), 2) if assets_count > 0 else 0