from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField("Телефон", max_length=20, blank=True, null=True)
    role = models.CharField(
        "Роль",
        max_length=20,
        choices=[
            ('admin', 'Администратор'),
            ('manager', 'Менеджер'),
            ('viewer', 'Просмотр')
        ],
        default='viewer'
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
