from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Кастомная модель пользователя с расширенными полями.
    Объединяет функционал из обоих вариантов:
    - Система ролей (admin/manager/client)
    - Контактные данные
    - Аватар
    - Верификация
    - Индексация для оптимизации
    """

    # Система ролей
    ROLES = (
        ('admin', _('Administrator')),
        ('manager', _('Manager')),
        ('client', _('Client')),
    )

    # Контактные данные
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("Телефон"),
        help_text=_("Формат: +79991234567")
    )

    # Системная роль
    role = models.CharField(
        max_length=10,
        choices=ROLES,
        default='client',
        verbose_name=_("Роль пользователя"),
        help_text=_("Определяет уровень доступа в системе")
    )

    # Аватар пользователя
    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True,
        null=True,
        verbose_name=_("Аватар"),
        help_text=_("Изображение профиля пользователя")
    )

    # Статус верификации
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("Верифицирован"),
        help_text=_("Подтвержден ли аккаунт пользователя")
    )

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        """Строковое представление пользователя"""
        name_parts = []

        if self.get_full_name():
            name_parts.append(self.get_full_name())

        name_parts.append(f"({self.username})")

        if self.role != 'client':
            name_parts.append(f"[{self.get_role_display()}]")

        return ' '.join(name_parts)

    @property
    def display_name(self):
        """Возвращает отображаемое имя пользователя"""
        return self.get_full_name() or self.username

    @property
    def is_administrator(self):
        """Проверяет, является ли пользователь администратором"""
        return self.role == 'admin'

    @property
    def is_manager(self):
        """Проверяет, является ли пользователь менеджером"""
        return self.role == 'manager'

    @property
    def is_client(self):
        """Проверяет, является ли пользователь клиентом"""
        return self.role == 'client'