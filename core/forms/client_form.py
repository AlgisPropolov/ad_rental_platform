from django import forms
from core.models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'inn', 'contact_person', 'phone', 'email']
        labels = {
            'name': 'Название компании',
            'inn': 'ИНН',
            'contact_person': 'Контактное лицо',
            'phone': 'Телефон',
            'email': 'E-mail',
        }
