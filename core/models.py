from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError


class BaseModel(models.Model):
    """Абстрактная базовая модель с общими полями"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    class Meta:
        abstract = True


class Client(BaseModel):
    """Модель клиента (рекламодателя)"""
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Номер телефона должен быть в формате: '+79991234567'")
    )

    name = models.CharField(max_length=255, verbose_name=_("Название компании"))
    inn = models.CharField(
        max_length=12,
        verbose_name=_("ИНН"),
        blank=True,
        null=True,
        unique=True,
        validators=[RegexValidator(r'^\d{10,12}$', _("Неверный формат ИНН"))]
    )
    contact_person = models.CharField(max_length=255, verbose_name=_("Контактное лицо"))
    phone = models.CharField(
        max_length=20,
        verbose_name=_("Телефон"),
        validators=[phone_regex]
    )
    email = models.EmailField(verbose_name=_("Email"))
    is_vip = models.BooleanField(default=False, verbose_name=_("VIP клиент"))
    notes = models.TextField(
        verbose_name=_("Примечания"),
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.name} ({self.contact_person})"

    class Meta:
        verbose_name = _("Клиент")
        verbose_name_plural = _("Клиенты")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['inn']),
            models.Index(fields=['is_vip']),
        ]


class Asset(BaseModel):
    """Модель рекламного актива"""

    class AssetType(models.TextChoices):
        BUS = 'bus', _('Автобус')
        BUS_STOP = 'bus_stop', _('Остановка')
        SCREEN = 'screen', _('Медиаэкран')
        BILLBOARD = 'billboard', _('Билборд')
        DIGITAL = 'digital', _('Цифровой экран')

    class Zone(models.TextChoices):
        CENTER = 'center', _('Центр')
        NORTH = 'north', _('Север')
        SOUTH = 'south', _('Юг')
        EAST = 'east', _('Восток')
        WEST = 'west', _('Запад')

    name = models.CharField(max_length=255, verbose_name=_("Название"))
    asset_type = models.CharField(
        max_length=20,
        choices=AssetType.choices,
        verbose_name=_("Тип актива")
    )
    zone = models.CharField(
        max_length=10,
        choices=Zone.choices,
        default=Zone.CENTER,
        verbose_name=_("Зона")
    )
    location = models.CharField(max_length=255, verbose_name=_("Местоположение"))
    daily_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Дневная ставка"),
        validators=[MinValueValidator(0)],
        default=0.00
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    notes = models.TextField(blank=True, verbose_name=_("Примечания"))

    def clean(self):
        if self.daily_rate <= 0:
            raise ValidationError(_("Дневная ставка должна быть положительной"))

    def __str__(self):
        return f"{self.get_asset_type_display()} - {self.location} ({self.get_zone_display()})"

    class Meta:
        verbose_name = _("Рекламный актив")
        verbose_name_plural = _("Рекламные активы")
        ordering = ['name']
        indexes = [
            models.Index(fields=['asset_type']),
            models.Index(fields=['zone']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['location', 'asset_type'],
                name='unique_asset_location'
            )
        ]


class AvailabilitySlot(BaseModel):
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
    reserved_by = models.ForeignKey(
        'Contract',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reserved_slots',
        verbose_name=_("Зарезервировано договором")
    )

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError(_("Дата окончания не может быть раньше даты начала"))

        overlapping_slots = AvailabilitySlot.objects.filter(
            asset=self.asset,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        ).exclude(pk=self.pk)

        if overlapping_slots.exists():
            raise ValidationError(_("Период пересекается с существующим слотом"))

    def __str__(self):
        status = _("Доступен") if self.is_available else _("Занят ({})").format(self.reserved_by)
        return f"{self.asset} | {self.start_date} - {self.end_date} | {status}"

    class Meta:
        verbose_name = _("Слот доступности")
        verbose_name_plural = _("Слоты доступности")
        ordering = ['-start_date']
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='check_slot_dates'
            )
        ]


class Deal(BaseModel):
    """Модель сделки"""

    class Status(models.TextChoices):
        NEW = 'new', _('Новая')
        IN_PROGRESS = 'in_progress', _('В работе')
        APPROVAL = 'approval', _('На согласовании')
        WON = 'won', _('Успешная')
        LOST = 'lost', _('Проваленная')
        ARCHIVED = 'archived', _('Архивированная')

    title = models.CharField(max_length=255, verbose_name=_("Название сделки"))
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        verbose_name=_("Клиент"),
        related_name='deals'
    )
    manager = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        verbose_name=_("Менеджер"),
        related_name='deals'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name=_("Статус")
    )
    expected_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Ожидаемая сумма"),
        validators=[MinValueValidator(0)]
    )
    probability = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Вероятность успеха (%)"),
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата закрытия"))

    @property
    def duration_days(self):
        if self.closed_at:
            return (self.closed_at - self.created_at).days
        return (timezone.now() - self.created_at).days

    def clean(self):
        if self.closed_at and self.closed_at.date() < self.created_at.date():
            raise ValidationError(_("Дата закрытия не может быть раньше даты создания"))

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    class Meta:
        verbose_name = _("Сделка")
        verbose_name_plural = _("Сделки")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['client']),
            models.Index(fields=['manager']),
            models.Index(fields=['probability']),
        ]


class Contract(BaseModel):
    """Модель договора"""

    class PaymentType(models.TextChoices):
        FULL = 'full', _('Полная предоплата')
        PARTIAL = 'partial', _('Частичная предоплата')
        POSTPAY = 'postpay', _('Постоплата')

    number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Номер договора")
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        verbose_name=_("Клиент"),
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
    assets = models.ManyToManyField(
        Asset,
        through='ContractAsset',
        verbose_name=_("Активы")
    )
    start_date = models.DateField(verbose_name=_("Дата начала"))
    end_date = models.DateField(verbose_name=_("Дата окончания"))
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Общая сумма"),
        validators=[MinValueValidator(0)],
        default=0.00  # Добавлено значение по умолчанию
    )
    payment_type = models.CharField(
        max_length=10,
        choices=PaymentType.choices,
        default=PaymentType.FULL,
        verbose_name=_("Тип оплаты")
    )
    signed = models.BooleanField(default=False, verbose_name=_("Подписан"))
    signed_date = models.DateField(null=True, blank=True, verbose_name=_("Дата подписания"))
    is_active = models.BooleanField(default=True, verbose_name=_("Действующий"))

    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError(_("Дата окончания не может быть раньше даты начала"))

        if self.signed_date and self.signed_date < self.start_date:
            raise ValidationError(_("Дата подписания не может быть раньше даты начала"))

    def __str__(self):
        return f"Договор №{self.number} ({self.client})"

    class Meta:
        verbose_name = _("Договор")
        verbose_name_plural = _("Договоры")
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['number']),
            models.Index(fields=['client']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='end_date_after_start_date'
            )
        ]


class ContractAsset(models.Model):
    """Промежуточная модель для связи договора и активов"""
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='contract_assets',
        verbose_name=_("Договор")
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='contract_assets',
        verbose_name=_("Актив")
    )
    slot = models.ForeignKey(
        AvailabilitySlot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Слот доступности")
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Цена"),
        validators=[MinValueValidator(0)]
    )
    notes = models.TextField(blank=True, verbose_name=_("Примечания"))

    def __str__(self):
        return f"{self.asset} в договоре {self.contract.number}"

    class Meta:
        verbose_name = _("Актив договора")
        verbose_name_plural = _("Активы договоров")
        constraints = [
            models.UniqueConstraint(
                fields=['contract', 'asset', 'slot'],
                name='unique_contract_asset_slot'
            )
        ]


class Payment(BaseModel):
    """Модель платежа"""
    PAYMENT_METHODS = [
        ('cash', 'Наличные'),
        ('card', 'Карта'),
        ('transfer', 'Банковский перевод'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('completed', 'Завершён'),
        ('failed', 'Неудачный'),
    ]

    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_("Договор")
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Сумма"),
        validators=[MinValueValidator(0)]
    )
    date = models.DateField(verbose_name=_("Дата платежа"))
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        verbose_name=_("Способ оплаты")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_("Статус")
    )
    is_confirmed = models.BooleanField(default=False, verbose_name=_("Подтвержден"))
    confirmation_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Дата подтверждения")
    )
    notes = models.TextField(blank=True, verbose_name=_("Примечания"))
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("ID транзакции")
    )

    def clean(self):
        if self.date > timezone.now().date():
            raise ValidationError(_("Дата платежа не может быть в будущем"))

    def __str__(self):
        return f"Платёж {self.amount} от {self.date} (Договор №{self.contract.number})"

    class Meta:
        verbose_name = _("Платёж")
        verbose_name_plural = _("Платежи")
        ordering = ['-date']
        indexes = [
            models.Index(fields=['contract']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
            models.Index(fields=['is_confirmed']),
        ]


class DealTask(BaseModel):
    """Модель задачи по сделке"""

    class Priority(models.TextChoices):
        LOW = 'low', _('Низкий')
        MEDIUM = 'medium', _('Средний')
        HIGH = 'high', _('Высокий')
        CRITICAL = 'critical', _('Критичный')

    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name=_("Сделка")
    )
    assigned_to = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Исполнитель")
    )
    title = models.CharField(max_length=200, verbose_name=_("Заголовок"))
    description = models.TextField(verbose_name=_("Описание"))
    is_done = models.BooleanField(default=False, verbose_name=_("Выполнено"))
    due_date = models.DateField(verbose_name=_("Срок выполнения"))
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name=_("Приоритет")
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Дата выполнения")
    )

    def clean(self):
        if self.completed_at and not self.is_done:
            raise ValidationError(_("Дата выполнения указана, но задача не помечена как выполненная"))

        if self.due_date and self.due_date < timezone.now().date() and not self.is_done:
            raise ValidationError(_("Срок выполнения задачи уже прошел"))

    def save(self, *args, **kwargs):
        if self.is_done and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_priority_display()})"

    class Meta:
        verbose_name = _("Задача по сделке")
        verbose_name_plural = _("Задачи по сделкам")
        ordering = ['-due_date']
        indexes = [
            models.Index(fields=['deal']),
            models.Index(fields=['is_done']),
            models.Index(fields=['due_date']),
            models.Index(fields=['priority']),
        ]