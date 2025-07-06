from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import Asset


class AssetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        """Инициализация формы с дополнительными настройками"""
        super().__init__(*args, **kwargs)

        # Настройка обязательности полей
        self.fields['notes'].required = False

        # Оптимизация выпадающих списков
        self.fields['asset_type'].widget.attrs.update({
            'class': 'form-select select2',
            'data-placeholder': _('Выберите тип объекта')
        })

        self.fields['zone'].widget.attrs.update({
            'class': 'form-select select2',
            'data-placeholder': _('Выберите зону')
        })

    class Meta:
        model = Asset
        fields = ['name', 'asset_type', 'zone', 'location',
                  'daily_rate', 'is_active', 'notes']
        labels = {
            'name': _('Название объекта'),
            'asset_type': _('Тип объекта'),
            'zone': _('Зона'),
            'location': _('Местоположение'),
            'daily_rate': _('Дневная ставка (руб)'),
            'is_active': _('Активен для аренды'),
            'notes': _('Примечания'),
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Например: Билборд на Ленинском проспекте'),
                'autofocus': True
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Например: Москва, Ленинский пр-т, д. 42')
            }),
            'daily_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 500,
                'placeholder': _('5000')
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': _('Особенности размещения, ограничения и т.д.')
            }),
        }
        help_texts = {
            'daily_rate': _('Минимальная ставка: 500 руб/день'),
            'asset_type': _('Выберите из списка доступных типов'),
        }

    def clean_daily_rate(self):
        """Валидация дневной ставки"""
        daily_rate = self.cleaned_data.get('daily_rate', 0)

        if daily_rate < 500:
            raise ValidationError(
                _("Минимальная дневная ставка - 500 рублей")
            )

        if daily_rate > 1000000:
            raise ValidationError(
                _("Слишком высокая ставка. Максимум 1 000 000 рублей")
            )

        return round(daily_rate, 2)

    def clean_name(self):
        """Валидация названия"""
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 3:
            raise ValidationError(
                _("Название слишком короткое (мин. 3 символа)")
            )
        return name

    def clean(self):
        """Общая валидация формы"""
        cleaned_data = super().clean()

        # Проверка уникальности названия в зоне
        name = cleaned_data.get('name')
        zone = cleaned_data.get('zone')

        if name and zone:
            qs = Asset.objects.filter(
                name__iexact=name,
                zone=zone
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise ValidationError(
                    _("Актив с таким названием уже существует в этой зоне")
                )

        return cleaned_data