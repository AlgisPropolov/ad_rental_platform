from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'role', 'password1', 'password2')
        widgets = {
            'role': forms.Select(choices=User.ROLES)
        }


class ProfileUpdateForm(UserChangeForm):
    password = None  # Убираем поле смены пароля

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'role', 'first_name', 'last_name')
        widgets = {
            'role': forms.Select(choices=User.ROLES)
        }