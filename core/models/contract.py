from django.db import models
from .client import Client
from .asset import Asset
from .deal import Deal

class Contract(models.Model):
    deal = models.OneToOneField(Deal, on_delete=models.CASCADE, related_name="contract", verbose_name="Сделка", null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Контрагент")
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name="Объект рекламы")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    signed = models.BooleanField(default=False, verbose_name="Подписан")
    number = models.CharField(max_length=100, verbose_name="Номер договора", blank=True)
    signed_date = models.DateField(null=True, blank=True, verbose_name="Дата подписания")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Договор {self.number or ''} — {self.client.name} / {self.asset.name}"

    class Meta:
        verbose_name = "Договор"
        verbose_name_plural = "Договоры"
