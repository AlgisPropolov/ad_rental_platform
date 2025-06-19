from django.db import models

class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название компании")
    inn = models.CharField(max_length=12, verbose_name="ИНН", blank=True, null=True)
    contact_person = models.CharField(max_length=255, verbose_name="Контактное лицо", blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name="Телефон", blank=True, null=True)
    email = models.EmailField(verbose_name="E-mail", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Контрагент"
        verbose_name_plural = "Контрагенты"
