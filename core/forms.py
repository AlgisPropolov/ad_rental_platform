from django import forms
from django.utils import timezone
from core.models import Asset, DealTask
from django.utils.translation import gettext_lazy as _

class AssetForm(forms.ModelForm):
    """
    Форма для создания и редактирования активов
    """
    class Meta:
        model = Asset
        fields = ['name', 'asset_type', 'zone', 'location',
                 'daily_rate', 'is_active', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': _('Дополнительная информация об активе')
            }),
            'daily_rate': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0'
            }),
        }
        labels = {
            'daily_rate': _('Дневная ставка (руб)'),
        }
        help_texts = {
            'is_active': _('Отметьте, если актив доступен для аренды'),
        }

    def clean_daily_rate(self):
        """Валидация дневной ставки"""
        daily_rate = self.cleaned_data.get('daily_rate')
        if daily_rate <= 0:
            raise forms.ValidationError(_('Ставка должна быть положительной'))
        return daily_rate


class TaskForm(forms.ModelForm):
    """
    Форма для работы с задачами по сделкам
    """
    class Meta:
        model = DealTask
        fields = ['deal', 'assigned_to', 'title', 'description', 'due_date', 'priority']
        widgets = {
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'due_date': _('Срок выполнения'),
            'priority': _('Приоритет'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['deal'].queryset = self.fields['deal'].queryset.select_related('client')
        self.fields['assigned_to'].queryset = self.fields['assigned_to'].queryset.filter(is_active=True)

    def clean_due_date(self):
        """Валидация даты выполнения"""
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < timezone.now().date():
            raise forms.ValidationError(_('Дата выполнения не может быть в прошлом'))
        return due_date