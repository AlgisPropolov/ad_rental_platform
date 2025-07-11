from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db.models import Q, F, Count, Case, When, ExpressionWrapper, DurationField, Min

User = get_user_model()

class BaseModel(models.Model):
    """Абстрактная базовая модель с общими полями"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class ClientManager(models.Manager):
    """Менеджер для клиентов с бизнес-логикой"""
    def active(self):
        return self.filter(is_active=True)

    def vip(self):
        return self.active().filter(is_vip=True)

    def with_active_contracts(self):
        return self.annotate(
            active_contracts=Count(
                'contracts',
                filter=Q(contracts__is_active=True) &
                       Q(contracts__start_date__lte=timezone.now().date()) &
                       Q(contracts__end_date__gte=timezone.now().date())
            )
        )

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
    phone = models.CharField(max_length=20, validators=[phone_regex], verbose_name=_("Телефон"))
    email = models.EmailField(verbose_name=_("Email"))
    is_vip = models.BooleanField(default=False, verbose_name=_("VIP клиент"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    notes = models.TextField(
        blank=True,
        default='',  # Добавлено значение по умолчанию
        verbose_name=_("Примечания")
    )
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients',
        verbose_name=_("Ответственный менеджер")
    )

    objects = ClientManager()

    def __str__(self):
        return f"{self.name} ({self.contact_person})"

    class Meta:
        verbose_name = _("Клиент")
        verbose_name_plural = _("Клиенты")
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['inn']),
            models.Index(fields=['is_vip']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'contact_person'],
                name='unique_client_contact'
            )
        ]

class AssetQuerySet(models.QuerySet):
    """Кастомный QuerySet для активов"""
    def active(self):
        return self.filter(is_active=True)

    def by_type(self, asset_type):
        return self.filter(asset_type=asset_type)

    def available_for_period(self, start_date, end_date):
        return self.exclude(
            availability_slots__start_date__lte=end_date,
            availability_slots__end_date__gte=start_date,
            availability_slots__is_available=False
        ).distinct()

    def with_contracts_count(self):
        return self.annotate(contracts_count=Count('contracts'))

class Asset(BaseModel):
    """Модель рекламного актива"""
    class AssetType(models.TextChoices):
        BUS = 'bus', _('Автобус')
        BUS_STOP = 'bus_stop', _('Остановка')
        SCREEN = 'screen', _('Медиаэкран')
        BILLBOARD = 'billboard', _('Билборд')

    class Zone(models.TextChoices):
        CENTER = 'center', _('Центр')
        NORTH = 'north', _('Север')
        SOUTH = 'south', _('Юг')
        EAST = 'east', _('Восток')
        WEST = 'west', _('Запад')

    name = models.CharField(max_length=255, verbose_name=_("Название"))
    asset_type = models.CharField(max_length=20, choices=AssetType.choices, verbose_name=_("Тип актива"))
    zone = models.CharField(max_length=10, choices=Zone.choices, default=Zone.CENTER, verbose_name=_("Зона"))
    location = models.CharField(max_length=255, verbose_name=_("Местоположение"))
    daily_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Дневная ставка"),
        validators=[MinValueValidator(0)]
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    notes = models.TextField(blank=True, verbose_name=_("Примечания"))
    tags = models.ManyToManyField('Tag', blank=True, related_name='assets', verbose_name=_("Теги"))

    objects = AssetQuerySet.as_manager()

    def clean(self):
        if self.daily_rate <= 0:
            raise ValidationError(_("Дневная ставка должна быть положительной"))

    def current_contract(self):
        return self.contracts.filter(
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date(),
            is_active=True
        ).first()

    def __str__(self):
        return f"{self.get_asset_type_display()} - {self.location} ({self.get_zone_display()})"

    class Meta:
        verbose_name = _("Рекламный актив")
        verbose_name_plural = _("Рекламные активы")
        indexes = [
            models.Index(fields=['asset_type']),
            models.Index(fields=['zone']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['location', 'asset_type'],
                name='unique_asset_location'
            ),
            models.CheckConstraint(
                check=Q(daily_rate__gte=0),
                name='daily_rate_positive'
            )
        ]

class Tag(models.Model):
    """Модель тегов для активов"""
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Название"))
    color = models.CharField(
        max_length=7,
        default='#6c757d',
        verbose_name=_("Цвет (HEX)"),
        validators=[RegexValidator(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', _("Неверный формат цвета"))]
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Тег")
        verbose_name_plural = _("Теги")

class AvailabilitySlotQuerySet(models.QuerySet):
    """Кастомный QuerySet для слотов доступности"""
    def available(self):
        return self.filter(is_available=True)

    def for_period(self, start_date, end_date):
        return self.filter(
            start_date__lte=end_date,
            end_date__gte=start_date
        )

    def overlapping(self, asset, start_date, end_date):
        return self.for_period(start_date, end_date).filter(asset=asset)

class AvailabilitySlot(BaseModel):
    """Модель слота доступности"""
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

    objects = AvailabilitySlotQuerySet.as_manager()

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError(_("Дата окончания не может быть раньше даты начала"))

        if self.is_available and self.reserved_by:
            raise ValidationError(_("Доступный слот не может быть зарезервирован"))

        overlapping_slots = AvailabilitySlot.objects.overlapping(
            self.asset,
            self.start_date,
            self.end_date
        ).exclude(pk=self.pk)

        if overlapping_slots.exists():
            raise ValidationError(_("Период пересекается с существующим слотом"))

    def duration_days(self):
        return (self.end_date - self.start_date).days

    def __str__(self):
        status = _("Доступен") if self.is_available else _("Занят")
        return f"{self.asset} | {self.start_date} - {self.end_date} | {status}"

    class Meta:
        verbose_name = _("Слот доступности")
        verbose_name_plural = _("Слоты доступности")
        constraints = [
            models.CheckConstraint(
                check=Q(end_date__gte=F('start_date')),
                name='check_slot_dates'
            )
        ]

class DealQuerySet(models.QuerySet):
    """Кастомный QuerySet для модели Deal"""
    def active(self):
        return self.exclude(status__in=[Deal.Status.WON, Deal.Status.LOST, Deal.Status.ARCHIVED])

    def won(self):
        return self.filter(status=Deal.Status.WON)

    def by_manager(self, manager):
        return self.filter(manager=manager)

    def with_duration(self):
        return self.annotate(
            duration=models.Case(
                models.When(
                    closed_at__isnull=False,
                    then=models.ExpressionWrapper(
                        models.F('closed_at') - models.F('created_at'),
                        output_field=models.DurationField()
                    )
                ),
                default=models.ExpressionWrapper(
                    timezone.now() - models.F('created_at'),
                    output_field=models.DurationField()
                ),
                output_field=models.DurationField()
            )
        )

class Deal(BaseModel):
    """Модель сделки с расширенной бизнес-логикой"""

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
        User,
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

    objects = DealQuerySet.as_manager()

    @property
    def duration_days(self):
        if self.closed_at:
            return (self.closed_at - self.created_at).days
        return (timezone.now() - self.created_at).days

    def clean(self):
        if self.closed_at and self.closed_at.date() < self.created_at.date():
            raise ValidationError(_("Дата закрытия не может быть раньше даты создания"))

        if self.status == Deal.Status.WON and not self.closed_at:
            self.closed_at = timezone.now()

    def save(self, *args, **kwargs):
        if self.status in [Deal.Status.WON, Deal.Status.LOST] and not self.closed_at:
            self.closed_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    class Meta:
        verbose_name = _("Сделка")
        verbose_name_plural = _("Сделки")
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['client']),
            models.Index(fields=['manager']),
            models.Index(fields=['probability']),
        ]
        permissions = [
            ('can_change_deal_status', _("Может изменять статус сделки")),
        ]

class ContractQuerySet(models.QuerySet):
    """Кастомный QuerySet для модели Contract"""
    def active(self):
        return self.filter(
            is_active=True,
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        )

    def expired(self):
        return self.filter(end_date__lt=timezone.now().date())

    def by_client(self, client):
        return self.filter(client=client)

    def with_duration(self):
        return self.annotate(
            duration=models.F('end_date') - models.F('start_date')
        )

class Contract(BaseModel):
    """Модель договора с расширенной бизнес-логикой"""

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
        validators=[MinValueValidator(0)]
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
    document = models.FileField(
        upload_to='contracts/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name=_("Скан договора")
    )

    objects = ContractQuerySet.as_manager()

    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days

    @property
    def days_remaining(self):
        return max((self.end_date - timezone.now().date()).days, 0)

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError(_("Дата окончания не может быть раньше даты начала"))

        if self.signed_date and self.signed_date < self.start_date:
            raise ValidationError(_("Дата подписания не может быть раньше даты начала"))

        if self.signed and not self.signed_date:
            self.signed_date = timezone.now().date()

    def save(self, *args, **kwargs):
        if self.signed and not self.signed_date:
            self.signed_date = timezone.now().date()
        super().save(*args, **kwargs)

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
        permissions = [
            ('can_upload_contract', _("Может загружать скан договора")),
        ]

class ContractAsset(models.Model):
    """Промежуточная модель для связи договора и активов с расширенной логикой"""
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
    created_at = models.DateTimeField(
        verbose_name=_("Дата создания"),
        default=timezone.now,  # Исправлено: убрано auto_now_add, добавлен default
    )

    def clean(self):
        if self.slot and self.slot.asset != self.asset:
            raise ValidationError(_("Слот доступности не принадлежит выбранному активу"))

        if self.slot and not self.slot.is_available:
            raise ValidationError(_("Выбранный слот уже занят"))

    def save(self, *args, **kwargs):
        if self.slot:
            self.slot.is_available = False
            self.slot.reserved_by = self.contract
            self.slot.save()
        if not self.id and not self.created_at:  # Установка даты только для новых объектов
            self.created_at = timezone.now()
        super().save(*args, **kwargs)

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

class PaymentQuerySet(models.QuerySet):
    """Кастомный QuerySet для модели Payment"""
    def confirmed(self):
        return self.filter(is_confirmed=True)

    def unconfirmed(self):
        return self.filter(is_confirmed=False)

    def by_period(self, start_date, end_date):
        return self.filter(date__gte=start_date, date__lte=end_date)

    def by_contract(self, contract):
        return self.filter(contract=contract)

class Payment(BaseModel):
    """Модель платежа с расширенной бизнес-логикой"""

    class PaymentMethod(models.TextChoices):
        CASH = 'cash', _('Наличные')
        CARD = 'card', _('Карта')
        TRANSFER = 'transfer', _('Банковский перевод')
        OTHER = 'other', _('Другое')

    class Status(models.TextChoices):
        PENDING = 'pending', _('Ожидает')
        COMPLETED = 'completed', _('Завершён')
        FAILED = 'failed', _('Неудачный')
        REFUNDED = 'refunded', _('Возвращён')

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
        choices=PaymentMethod.choices,
        verbose_name=_("Способ оплаты")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
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
    receipt = models.FileField(
        upload_to='payment_receipts/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name=_("Квитанция")
    )

    objects = PaymentQuerySet.as_manager()

    def clean(self):
        if self.date > timezone.now().date():
            raise ValidationError(_("Дата платежа не может быть в будущем"))

        if self.is_confirmed and not self.confirmation_date:
            self.confirmation_date = timezone.now()

        if self.status == Payment.Status.COMPLETED and not self.is_confirmed:
            self.is_confirmed = True

    def save(self, *args, **kwargs):
        if self.is_confirmed and not self.confirmation_date:
            self.confirmation_date = timezone.now()
        super().save(*args, **kwargs)

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
        permissions = [
            ('can_confirm_payment', _("Может подтверждать платежи")),
        ]

class DealTaskQuerySet(models.QuerySet):
    """Кастомный QuerySet для модели DealTask"""
    def active(self):
        return self.filter(is_done=False)

    def completed(self):
        return self.filter(is_done=True)

    def overdue(self):
        return self.active().filter(due_date__lt=timezone.now().date())

    def high_priority(self):
        return self.filter(priority__in=[DealTask.Priority.HIGH, DealTask.Priority.CRITICAL])

    def by_deal(self, deal):
        return self.filter(deal=deal)

    def by_assignee(self, user):
        return self.filter(assigned_to=user)

class DealTask(BaseModel):
    """Модель задачи по сделке с расширенной бизнес-логикой"""

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
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
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

    objects = DealTaskQuerySet.as_manager()

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
            models.Index(fields=['assigned_to']),
        ]
        permissions = [
            ('can_reassign_task', _("Может переназначать задачи")),
        ]