from django.db import models
from django.utils import timezone
from users.models import User  # Предполагаем, что у вас есть кастомная модель пользователя


class Client(models.Model):
    """Модель клиента (рекламодателя)"""
    name = models.CharField(max_length=255, verbose_name="Название компании")
    inn = models.CharField(max_length=20, verbose_name="ИНН", blank=True, null=True)
    contact_person = models.CharField(max_length=255, verbose_name="Контактное лицо")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ['-created_at']


class Asset(models.Model):
    """Модель рекламного актива"""
    ASSET_TYPES = [
        ('bus', 'Автобус'),
        ('bus_stop', 'Остановка'),
        ('screen', 'Медиаэкран')
    ]

    name = models.CharField(max_length=255, verbose_name="Название")
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES, verbose_name="Тип актива")
    location = models.CharField(max_length=255, verbose_name="Местоположение")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"{self.get_asset_type_display()} - {self.location}"

    class Meta:
        verbose_name = "Рекламный актив"
        verbose_name_plural = "Рекламные активы"
        ordering = ['name']


class AvailabilitySlot(models.Model):
    """Модель доступности актива"""
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='availability_slots',
        verbose_name="Актив"
    )
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    is_available = models.BooleanField(default=True, verbose_name="Доступен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"{self.asset} с {self.start_date} по {self.end_date}"

    class Meta:
        verbose_name = "Слот доступности"
        verbose_name_plural = "Слоты доступности"
        ordering = ['-start_date']
        unique_together = ['asset', 'start_date', 'end_date']


class Deal(models.Model):
    """Модель сделки"""
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('won', 'Успешная'),
        ('lost', 'Проваленная'),
        ('archived', 'Архивированная')
    ]

    title = models.CharField(max_length=255, verbose_name="Название сделки")
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name="Клиент",
        related_name='deals'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата закрытия")

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Сделка"
        verbose_name_plural = "Сделки"
        ordering = ['-created_at']


class Contract(models.Model):
    """Модель договора"""
    number = models.CharField(max_length=50, unique=True, verbose_name="Номер договора")
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name="Клиент",
        related_name='contracts'
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        verbose_name="Актив",
        related_name='contracts'
    )
    deal = models.ForeignKey(
        Deal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Сделка",
        related_name='contracts'
    )
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость")
    signed = models.BooleanField(default=False, verbose_name="Подписан")
    signed_date = models.DateField(null=True, blank=True, verbose_name="Дата подписания")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"Договор №{self.number} ({self.client})"

    class Meta:
        verbose_name = "Договор"
        verbose_name_plural = "Договоры"
        ordering = ['-start_date']
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='end_date_after_start_date'
            )
        ]


class Payment(models.Model):
    """Модель платежа"""
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Договор"
    )
    date = models.DateField(verbose_name="Дата платежа")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    is_confirmed = models.BooleanField(default=False, verbose_name="Подтвержден")
    confirmation_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата подтверждения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"Платёж {self.amount} от {self.date} (Договор №{self.contract.number})"

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ['-date']


class DealTask(models.Model):
    """Модель задачи по сделке"""
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий')
    ]

    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name="Сделка"
    )
    description = models.TextField(verbose_name="Описание")
    is_done = models.BooleanField(default=False, verbose_name="Выполнено")
    due_date = models.DateField(verbose_name="Срок выполнения")
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name="Приоритет"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"Задача по сделке {self.deal.title} ({self.get_priority_display()})"

    class Meta:
        verbose_name = "Задача по сделке"
        verbose_name_plural = "Задачи по сделкам"
        ordering = ['-due_date']