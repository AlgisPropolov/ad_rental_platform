from django.db import models
from .deal import Deal

class DealTask(models.Model):
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, verbose_name="Сделка")
    description = models.CharField(max_length=255, verbose_name="Описание задачи")
    is_done = models.BooleanField(default=False, verbose_name="Выполнено")
    due_date = models.DateField(verbose_name="Срок выполнения", null=True, blank=True)

    def __str__(self):
        return f"Задача для сделки: {self.deal.title}"

    class Meta:
        verbose_name = "Задача по сделке"
        verbose_name_plural = "Задачи по сделкам"
