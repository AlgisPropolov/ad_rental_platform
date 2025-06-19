from django.db import models
from .client import Client
from .asset import Asset

class Deal(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название сделки")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Контрагент")
    assets = models.ManyToManyField(Asset, verbose_name="Объекты рекламы")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('draft', 'Черновик'),
            ('sent', 'Отправлено КП'),
            ('signed', 'Подписан договор'),
            ('closed', 'Завершено')
        ],
        default='draft',
        verbose_name="Статус"
    )

    def __str__(self):
        return f"{self.title} ({self.client.name})"

    class Meta:
        verbose_name = "Сделка"
        verbose_name_plural = "Сделки"
