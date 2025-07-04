from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from users.models import User


class Client(models.Model):
    """Модель клиента (рекламодателя) с расширенными возможностями"""

    class Meta:
        verbose_name = _("Клиент")
        verbose_name_plural = _("Клиенты")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['inn']),
            models.Index(fields=['created_at']),
        ]

    name = models.CharField(
        max_length=255,
        verbose_name=_("Название компании"),
        help_text=_("Полное официальное название компании")
    )
    inn = models.CharField(
        max_length=20,
        verbose_name=_("ИНН"),
        blank=True,
        null=True,
        unique=True
    )
    contact_person = models.CharField(
        max_length=255,
        verbose_name=_("Контактное лицо")
    )
    phone = models.CharField(
        max_length=20,
        verbose_name=_("Телефон")
    )
    email = models.EmailField(
        verbose_name=_("Email")
    )
    discount = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Скидка (%)"),
        validators=[models.MaxValueValidator(100)]
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("Дополнительная информация")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления")
    )
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='clients',
        verbose_name=_("Менеджер")
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('client-detail', kwargs={'pk': self.pk})

    def clean(self):
        if self.inn and len(self.inn) not in (10, 12):
            raise ValidationError(_("ИНН должен содержать 10 или 12 цифр"))


class ContractQuerySet(models.QuerySet):
    """Кастомный QuerySet для договоров"""

    def active(self):
        return self.filter(
            end_date__gte=timezone.now().date(),
            signed=True
        )

    def expired(self):
        return self.filter(
            end_date__lt=timezone.now().date()
        )

    def unsigned(self):
        return self.filter(signed=False)


class Contract(models.Model):
    """Модель договора с расширенной бизнес-логикой"""

    class Status(models.TextChoices):
        DRAFT = 'draft', _('Черновик')
        ACTIVE = 'active', _('Активен')
        SUSPENDED = 'suspended', _('Приостановлен')
        COMPLETED = 'completed', _('Завершен')
        TERMINATED = 'terminated', _('Расторгнут')

    objects = ContractQuerySet.as_manager()

    class Meta:
        verbose_name = _("Договор")
        verbose_name_plural = _("Договоры")
        ordering = ['-start_date']
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='end_date_after_start_date'
            ),
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name='price_positive'
            )
        ]
        permissions = [
            ("export_contract", "Can export contract data"),
            ("terminate_contract", "Can terminate contracts"),
        ]

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
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_("Статус")
    )
    start_date = models.DateField(
        verbose_name=_("Дата начала")
    )
    end_date = models.DateField(
        verbose_name=_("Дата окончания")
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Стоимость")
    )
    signed = models.BooleanField(
        default=False,
        verbose_name=_("Подписан")
    )
    signed_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Дата подписания")
    )
    termination_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Дата расторжения")
    )
    termination_reason = models.TextField(
        blank=True,
        verbose_name=_("Причина расторжения")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления")
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_contracts',
        verbose_name=_("Создатель договора")
    )

    def __str__(self):
        return f"{_('Договор')} №{self.number} ({self.client})"

    def get_absolute_url(self):
        return reverse('contract-detail', kwargs={'pk': self.pk})

    @property
    def duration_days(self):
        """Количество дней действия договора"""
        return (self.end_date - self.start_date).days + 1

    @property
    def days_remaining(self):
        """Осталось дней до окончания"""
        return (self.end_date - timezone.now().date()).days

    @property
    def total_paid(self):
        """Сумма подтвержденных платежей"""
        return sum(
            p.amount for p in self.payments.filter(is_confirmed=True)
        )

    @property
    def payment_status(self):
        """Статус оплаты"""
        if self.total_paid >= self.price:
            return _("Оплачен полностью")
        elif self.total_paid > 0:
            return _("Частичная оплата")
        return _("Не оплачен")

    def clean(self):
        errors = {}

        # Проверка дат
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                errors['end_date'] = _("Дата окончания не может быть раньше даты начала")

            if self.termination_date and (
                self.termination_date < self.start_date or
                self.termination_date > self.end_date
            ):
                errors['termination_date'] = _("Дата расторжения должна быть в периоде действия договора")

        # Проверка статуса
        if self.signed and not self.signed_date:
            errors['signed_date'] = _("Укажите дату подписания для подписанного договора")

        if errors:
            raise ValidationError(errors)


class Payment(models.Model):
    """Модель платежа с улучшенной логикой"""

    class PaymentMethod(models.TextChoices):
        CASH = 'cash', _('Наличные')
        BANK_TRANSFER = 'bank', _('Банковский перевод')
        CARD = 'card', _('Карта')
        OTHER = 'other', _('Другое')

    class Meta:
        verbose_name = _("Платёж")
        verbose_name_plural = _("Платежи")
        ordering = ['-date']
        get_latest_by = 'date'

    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_("Договор")
    )
    date = models.DateField(
        verbose_name=_("Дата платежа"),
        default=timezone.now
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Сумма")
    )
    method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
        default=PaymentMethod.BANK_TRANSFER,
        verbose_name=_("Способ оплаты")
    )
    is_confirmed = models.BooleanField(
        default=False,
        verbose_name=_("Подтвержден")
    )
    confirmation_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Дата подтверждения")
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("ID транзакции")
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("Комментарий")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления")
    )
    confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_payments',
        verbose_name=_("Подтвердил")
    )

    def __str__(self):
        return f"{self.amount} {_('от')} {self.date} ({self.contract})"

    def clean(self):
        if self.is_confirmed and not self.confirmation_date:
            self.confirmation_date = timezone.now()

        if self.amount <= 0:
            raise ValidationError(_("Сумма платежа должна быть положительной"))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ContractDocument(models.Model):
    """Модель для хранения документов договора"""

    class DocumentType(models.TextChoices):
        CONTRACT = 'contract', _('Договор')
        ADDENDUM = 'addendum', _('Допсоглашение')
        ACT = 'act', _('Акт')
        OTHER = 'other', _('Прочее')

    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_("Договор")
    )
    document_type = models.CharField(
        max_length=10,
        choices=DocumentType.choices,
        default=DocumentType.CONTRACT,
        verbose_name=_("Тип документа")
    )
    file = models.FileField(
        upload_to='contracts/documents/%Y/%m/%d/',
        verbose_name=_("Файл")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания")
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents',
        verbose_name=_("Загрузил")
    )

    class Meta:
        verbose_name = _("Документ договора")
        verbose_name_plural = _("Документы договоров")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_document_type_display()} {_('для')} {self.contract}"