from django.db import models
from .asset import Asset

class AvailabilitySlot(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name="Объект")
    start_date = models.DateField(verbose_name="Начало периода")
    end_date = models.DateField(verbose_name="Конец периода")
    is_booked = models.BooleanField(default=False, verbose_name="Забронировано")

    def __str__(self):
        return f"{self.asset.name} ({self.start_date} — {self.end_date})"

    class Meta:
        verbose_name = "Период доступности"
        verbose_name_plural = "Шахматка доступности"
        ordering = ['start_date']
