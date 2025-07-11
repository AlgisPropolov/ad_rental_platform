from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.contrib.auth import get_user_model
from core.models import Asset, DealTask, Deal

User = get_user_model()

class AssetForm(forms.ModelForm):
    """
    Форма для работы с активами с расширенной валидацией и кастомизацией
    """

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Оптимизация queryset для зон (используем choices из модели)
        self.fields['zone'].choices = Asset.Zone.choices

        # Динамическое изменение полей
        if self.user and not self.user.is_superuser:
            self.fields['is_active'].disabled = True
            self.fields['daily_rate'].widget.attrs['readonly'] = True

    class Meta:
        model = Asset
        fields = ['name', 'asset_type', 'zone', 'location',
                 'daily_rate', 'is_active', 'notes', 'tags']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Например: Автобус 1234 или Экран на остановке Пушкина')
            }),
            'asset_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'zone': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Точное местоположение')
            }),
            'daily_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': _('Технические характеристики, особенности и т.д.')
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'data-placeholder': _('Выберите теги')
            })
        }
        labels = {
            'daily_rate': _('Дневная ставка (руб)'),
            'asset_type': _('Тип актива'),
        }
        help_texts = {
            'is_active': _('Только активные объекты доступны для аренды'),
            'zone': _('Географическая зона размещения'),
        }

    def clean_daily_rate(self):
        daily_rate = self.cleaned_data.get('daily_rate')
        if daily_rate <= 0:
            raise forms.ValidationError(_('Ставка должна быть положительной'))
        if daily_rate > 1000000:
            raise forms.ValidationError(_('Слишком большая ставка'))
        return round(daily_rate, 2)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Asset.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_('Актив с таким названием уже существует'))
        return name


class TaskForm(forms.ModelForm):
    """
    Форма для управления задачами по сделкам с расширенной логикой
    """

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Оптимизация queryset
        self.fields['deal'].queryset = Deal.objects.filter(
            Q(status='in_progress') | Q(pk=self.instance.deal.pk if self.instance.pk else None)
        )

        self.fields['assigned_to'].queryset = User.objects.filter(
            is_active=True,
            groups__name__in=['Менеджеры', 'Администраторы']
        )

        # Кастомизация полей
        self.fields['due_date'].widget.attrs.update({
            'min': timezone.now().date().isoformat()
        })

    class Meta:
        model = DealTask
        fields = ['deal', 'assigned_to', 'title', 'description', 'due_date', 'priority', 'is_done']
        widgets = {
            'deal': forms.Select(attrs={
                'class': 'form-select'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-select'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Краткое описание задачи')
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': _('Подробное описание задачи')
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_done': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'due_date': _('Срок выполнения'),
            'priority': _('Приоритет'),
            'is_done': _('Завершена'),
        }

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < timezone.now().date():
            raise forms.ValidationError(_('Дата выполнения не может быть в прошлом'))
        return due_date

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('is_done') and not cleaned_data.get('completed_at'):
            cleaned_data['completed_at'] = timezone.now()
        return cleaned_data


class AssetFilterForm(forms.Form):
    """
    Форма фильтрации активов для списка
    """
    ASSET_TYPE_CHOICES = [
        ('', _('Все типы')),
        *Asset.AssetType.choices
    ]

    asset_type = forms.ChoiceField(
        choices=ASSET_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'this.form.submit()'
        })
    )

    zone = forms.ChoiceField(
        choices=Asset.Zone.choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'this.form.submit()'
        })
    )

    is_active = forms.ChoiceField(
        choices=[
            ('', _('Все')),
            ('true', _('Активные')),
            ('false', _('Неактивные'))
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'this.form.submit()'
        })
    )

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Поиск по названию или местоположению')
        })
    )