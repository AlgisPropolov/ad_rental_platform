from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import User


class BaseModel(models.Model):
    """Абстрактная базовая модель с общими полями"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    class Meta:
        abstract = True


class Client(BaseModel):
    """Модель клиента (рекламодателя)"""
    name = models.CharField(max_length=255, verbose_name=_("Название компании"))
    contact_person = models.CharField(max_length=255, verbose_name=_("Контактное лицо"))
    phone = models.CharField(max_length=20, verbose_name=_("Телефон"))
    email = models.EmailField(verbose_name=_("Email"))
    is_vip = models.BooleanField(default=False, verbose_name=_("VIP клиент"))
    notes = models.TextField(blank=True, verbose_name=_("Примечания"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Клиент")
        verbose_name_plural = _("Клиенты")
        ordering = ['-created_at']


class AdSpace(BaseModel):
    """Модель рекламного места (актива)"""
    TYPE_CHOICES = [
        ('bus', _('Автобус')),
        ('bus_stop', _('Остановка')),
        ('screen', _('Медиаэкран')),
        ('billboard', _('Билборд')),
        ('digital', _('Цифровой экран'))
    ]

    ZONE_CHOICES = [
        ('center', _('Центр')),
        ('north', _('Север')),
        ('south', _('Юг')),
        ('east', _('Восток')),
        ('west', _('Запад'))
    ]

    name = models.CharField(max_length=255, verbose_name=_("Название"))
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name=_("Тип площадки")
    )
    zone = models.CharField(
        max_length=10,
        choices=ZONE_CHOICES,
        default='center',
        verbose_name=_("Зона")
    )
    location = models.CharField(max_length=255, verbose_name=_("Местоположение"))
    daily_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Дневная ставка"),
        validators=[MinValueValidator(0)],
        default=100.00  # Значение по умолчанию
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    notes = models.TextField(blank=True, verbose_name=_("Примечания"))

    def clean(self):
        if self.daily_rate < 0:
            raise ValidationError(_("Дневная ставка не может быть отрицательной"))

    def __str__(self):
        return f"{self.get_type_display()} - {self.location}"

    class Meta:
        verbose_name = _("Рекламная площадка")
        verbose_name_plural = _("Рекламные площадки")
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['location', 'type'],
                name='unique_adspace_location'
            )
        ]


class Contract(BaseModel):
    """Модель договора аренды"""
    PAYMENT_TYPES = [
        ('full', _('Полная предоплата')),
        ('partial', _('Частичная предоплата')),
        ('postpay', _('Постоплата'))
    ]

    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='contracts',
        verbose_name=_("Клиент")
    )
    ad_space = models.ForeignKey(
        AdSpace,
        on_delete=models.PROTECT,
        related_name='contracts',
        verbose_name=_("Рекламная площадка")
    )
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Менеджер")
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
        choices=PAYMENT_TYPES,
        default='full',
        verbose_name=_("Тип оплаты")
    )
    signed = models.BooleanField(default=False, verbose_name=_("Подписан"))
    signed_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Дата подписания")
    )

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError(_("Дата окончания не может быть раньше даты начала"))

        if self.signed_date and self.signed_date < self.start_date:
            raise ValidationError(_("Дата подписания не может быть раньше даты начала"))

    def __str__(self):
        return f"Договор №{self.id} - {self.client}"

    class Meta:
        verbose_name = _("Договор")
        verbose_name_plural = _("Договоры")
        ordering = ['-start_date']
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='contract_end_date_after_start'
            )
        ]


class Payment(BaseModel):
    """Модель платежа"""
    PAYMENT_METHODS = [
        ('cash', _('Наличные')),
        ('card', _('Карта')),
        ('transfer', _('Банковский перевод'))
    ]

    STATUS_CHOICES = [
        ('pending', _('Ожидает')),
        ('completed', _('Завершён')),
        ('failed', _('Неудачный'))
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
    payment_date = models.DateField(verbose_name=_("Дата платежа"))
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
        if self.payment_date > timezone.now().date():
            raise ValidationError(_("Дата платежа не может быть в будущем"))

    def __str__(self):
        return f"Платёж {self.amount} от {self.payment_date}"

    class Meta:
        verbose_name = _("Платёж")
        verbose_name_plural = _("Платежи")
        ordering = ['-payment_date']