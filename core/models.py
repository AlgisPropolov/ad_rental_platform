# C:\Users\user\Documents\GitHub\Task\ad_rental_platform\core\models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

class Client(models.Model):
    """Модель клиента (рекламодателя)"""
    name = models.CharField(max_length=255, verbose_name=_("Название компании"))
    inn = models.CharField(
        max_length=20,
        verbose_name=_("ИНН"),
        blank=True,
        null=True,
        unique=True
    )
    contact_person = models.CharField(max_length=255, verbose_name=_("Контактное лицо"))
    phone = models.CharField(max_length=20, verbose_name=_("Телефон"))
    email = models.EmailField(verbose_name=_("Email"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Клиент")
        verbose_name_plural = _("Клиенты")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['inn']),
        ]

class Asset(models.Model):
    """Модель рекламного актива"""
    class AssetType(models.TextChoices):
        BUS = 'bus', _('Автобус')
        BUS_STOP = 'bus_stop', _('Остановка')
        SCREEN = 'screen', _('Медиаэкран')

    name = models.CharField(max_length=255, verbose_name=_("Название"))
    asset_type = models.CharField(
        max_length=20,
        choices=AssetType.choices,
        verbose_name=_("Тип актива")
    )
    location = models.CharField(max_length=255, verbose_name=_("Местоположение"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    def __str__(self):
        return f"{self.get_asset_type_display()} - {self.location}"

    class Meta:
        verbose_name = _("Рекламный актив")
        verbose_name_plural = _("Рекламные активы")
        ordering = ['name']
        indexes = [
            models.Index(fields=['asset_type']),
            models.Index(fields=['is_active']),
        ]

class AvailabilitySlot(models.Model):
    """Модель доступности актива"""
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='availability_slots',
        verbose_name=_("Актив")
    )
    start_date = models.DateField(verbose_name=_("Дата начала"))
    end_date = models.DateField(verbose_name=_("Дата окончания"))
    is_available = models.BooleanField(default=True, verbose_name=_("Доступен"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    def __str__(self):
        return f"{self.asset} с {self.start_date} по {self.end_date}"

    class Meta:
        verbose_name = _("Слот доступности")
        verbose_name_plural = _("Слоты доступности")
        ordering = ['-start_date']
        unique_together = ['asset', 'start_date', 'end_date']
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='check_slot_dates'
            )
        ]

class Deal(models.Model):
    """Модель сделки"""
    class Status(models.TextChoices):
        NEW = 'new', _('Новая')
        IN_PROGRESS = 'in_progress', _('В работе')
        WON = 'won', _('Успешная')
        LOST = 'lost', _('Проваленная')
        ARCHIVED = 'archived', _('Архивированная')

    title = models.CharField(max_length=255, verbose_name=_("Название сделки"))
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name=_("Клиент"),
        related_name='deals'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name=_("Статус")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата закрытия"))

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    class Meta:
        verbose_name = _("Сделка")
        verbose_name_plural = _("Сделки")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['client']),
        ]

class Contract(models.Model):
    """Модель договора"""
    number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Номер договора")
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name=_("Клиент"),
        related_name='contracts'
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        verbose_name=_("Актив"),
        related_name='contracts'
    )
    deal = models.ForeignKey(
        Deal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Сделка"),
        related_name='contracts'
    )
    start_date = models.DateField(verbose_name=_("Дата начала"))
    end_date = models.DateField(verbose_name=_("Дата окончания"))
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Стоимость"),
        validators=[MinValueValidator(0)]
    )
    signed = models.BooleanField(default=False, verbose_name=_("Подписан"))
    signed_date = models.DateField(null=True, blank=True, verbose_name=_("Дата подписания"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    def __str__(self):
        return f"Договор №{self.number} ({self.client})"

    class Meta:
        verbose_name = _("Договор")
        verbose_name_plural = _("Договоры")
        ordering = ['-start_date']
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='end_date_after_start_date'
            )
        ]
        indexes = [
            models.Index(fields=['number']),
            models.Index(fields=['client']),
            models.Index(fields=['start_date', 'end_date']),
        ]

class Payment(models.Model):
    """Модель платежа"""
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_("Договор")
    )
    date = models.DateField(verbose_name=_("Дата платежа"))
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Сумма"),
        validators=[MinValueValidator(0)]
    )
    is_confirmed = models.BooleanField(default=False, verbose_name=_("Подтвержден"))
    confirmation_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Дата подтверждения")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    def __str__(self):
        return f"Платёж {self.amount} от {self.date} (Договор №{self.contract.number})"

    class Meta:
        verbose_name = _("Платёж")
        verbose_name_plural = _("Платежи")
        ordering = ['-date']
        indexes = [
            models.Index(fields=['contract']),
            models.Index(fields=['date']),
            models.Index(fields=['is_confirmed']),
        ]

class DealTask(models.Model):
    """Модель задачи по сделке"""
    class Priority(models.TextChoices):
        LOW = 'low', _('Низкий')
        MEDIUM = 'medium', _('Средний')
        HIGH = 'high', _('Высокий')

    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name=_("Сделка")
    )
    description = models.TextField(verbose_name=_("Описание"))
    is_done = models.BooleanField(default=False, verbose_name=_("Выполнено"))
    due_date = models.DateField(verbose_name=_("Срок выполнения"))
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name=_("Приоритет")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    def __str__(self):
        return f"Задача по сделке {self.deal.title} ({self.get_priority_display()})"

    class Meta:
        verbose_name = _("Задача по сделке")
        verbose_name_plural = _("Задачи по сделкам")
        ordering = ['-due_date']
        indexes = [
            models.Index(fields=['deal']),
            models.Index(fields=['is_done']),
            models.Index(fields=['due_date']),
        ]