from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import Client


class ClientForm(forms.ModelForm):
    phone = forms.CharField(
        label=_("Телефон"),
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message=_("Формат: '+79991234567'. Допустимы 9-15 цифр")
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+79991234567',
            'data-mask': '+7 (999) 999-99-99'
        })
    )

    class Meta:
        model = Client
        fields = ['name', 'inn', 'contact_person', 'phone', 'email', 'is_vip', 'notes']
        labels = {
            'name': _('Название компании'),
            'inn': _('ИНН'),
            'contact_person': _('Контактное лицо'),
            'phone': _('Телефон'),
            'email': _('Email'),
            'is_vip': _('VIP клиент'),
            'notes': _('Примечания'),
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('ООО "Ромашка"')
            }),
            'inn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1234567890'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Иванов Иван Иванович')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'client@example.com'
            }),
            'is_vip': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Дополнительная информация о клиенте...')
            }),
        }

    def clean_inn(self):
        """Валидация ИНН"""
        inn = self.cleaned_data.get('inn', '').strip()
        if inn:
            if len(inn) not in (10, 12) or not inn.isdigit():
                raise ValidationError(
                    _("ИНН должен содержать 10 или 12 цифр")
                )

            # Контрольная сумма для ИНН (базовая проверка)
            if len(inn) == 10:
                weights = [2, 4, 10, 3, 5, 9, 4, 6, 8]
                check_sum = sum(int(a) * b for a, b in zip(inn[:9], weights)) % 11 % 10
                if int(inn[9]) != check_sum:
                    raise ValidationError(_("Неверная контрольная сумма ИНН"))

        return inn

    def clean_email(self):
        """Проверка уникальности email"""
        email = self.cleaned_data.get('email', '').lower().strip()
        if email:
            qs = Client.objects.filter(email__iexact=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise ValidationError(
                    _("Клиент с таким email уже зарегистрирован")
                )
        return email

    def clean_name(self):
        """Валидация названия компании"""
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 3:
            raise ValidationError(
                _("Название должно содержать минимум 3 символа")
            )
        return name

    def clean(self):
        """Комплексная проверка данных"""
        cleaned_data = super().clean()

        # Дополнительные проверки при необходимости
        if cleaned_data.get('is_vip') and not cleaned_data.get('phone'):
            self.add_error('phone', _("Для VIP клиента телефон обязателен"))

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Настройка обязательности полей
        self.fields['notes'].required = False
        self.fields['inn'].required = False

        # Улучшенная стилизация полей
        for field_name, field in self.fields.items():
            if field_name == 'is_vip':
                continue
            if not isinstance(field.widget, (forms.CheckboxInput, forms.Textarea)):
                field.widget.attrs.setdefault('class', 'form-control')
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault('class', 'form-control')
                field.widget.attrs.setdefault('rows', 3)