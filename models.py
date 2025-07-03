from django.db import models
from users.models import User  # Предполагая, что у вас есть кастомная модель пользователя


class Client(models.Model):
    """Модель контрагента (рекламодателя)"""
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.name


class AdSpace(models.Model):
    """Модель рекламного места"""
    TYPE_CHOICES = [
        ('bus', 'Автобус'),
        ('bus_stop', 'Остановка'),
        ('screen', 'Медиаэкран')
    ]

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    location = models.CharField(max_length=255)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.location}"


class Contract(models.Model):
    """Модель договора аренды"""
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    ad_space = models.ForeignKey(AdSpace, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Договор №{self.id} - {self.client}"