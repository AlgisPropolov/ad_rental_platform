from django.db import models
from .asset import Asset

class AvailabilitySlot(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name="Объект")
    start_date = models.DateField(verbose_name="Начало")
    end_date = models.DateField(verbose_name="Конец")
    is_available = models.BooleanField(default=True, verbose_name="Свободен")

    def __str__(self):
        return f"{self.asset.name} ({self.start_date} — {self.end_date})"

    class Meta:
        verbose_name = "Слот доступности"
        verbose_name_plural = "Слоты доступности"
