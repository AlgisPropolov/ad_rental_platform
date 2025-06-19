from django.db import models
from .contract import Contract

class Payment(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, verbose_name="Договор")
    date = models.DateField(verbose_name="Дата оплаты")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    is_confirmed = models.BooleanField(default=False, verbose_name="Подтверждено")

    def __str__(self):
        return f"{self.amount} ₽ от {self.date} ({'Подтверждено' if self.is_confirmed else 'Ожидает'})"

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
