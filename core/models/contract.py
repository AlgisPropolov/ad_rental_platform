from django.db import models
from .client import Client
from .asset import Asset

class Contract(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Контрагент")
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name="Объект рекламы")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    signed = models.BooleanField(default=False, verbose_name="Подписан")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Договор с {self.client.name} — {self.asset.name}"

    class Meta:
        verbose_name = "Договор"
        verbose_name_plural = "Договоры"
