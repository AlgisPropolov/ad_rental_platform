from django.db import models

class Asset(models.Model):
    TYPE_CHOICES = [
        ('bus', 'Автобус'),
        ('stop', 'Остановка'),
        ('screen', 'Медиаэкран'),
    ]

    name = models.CharField(max_length=255, verbose_name="Название объекта")
    asset_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Тип")
    location = models.CharField(max_length=255, verbose_name="Местоположение")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_asset_type_display()})"

    class Meta:
        verbose_name = "Рекламный объект"
        verbose_name_plural = "Рекламные объекты"
