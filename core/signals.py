from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from .models import (
    Contract, ContractAsset, AvailabilitySlot,
    Payment, Deal, DealTask
)


@receiver(pre_save, sender=Contract)
def update_contract_total_amount(sender, instance, **kwargs):
    """
    Автоматически пересчитывает общую сумму договора при изменении активов
    и проверяет даты при сохранении
    """
    if instance.pk:
        # Пересчет суммы только для существующих договоров
        total = instance.contract_assets.aggregate(
            total=Sum('price')
        )['total'] or 0
        instance.total_amount = total

    # Валидация дат договора
    if instance.end_date < instance.start_date:
        raise ValidationError("Дата окончания договора не может быть раньше даты начала")


@receiver(post_save, sender=ContractAsset)
def update_slot_availability(sender, instance, created, **kwargs):
    """
    Обновляет статус слота доступности при привязке актива к договору
    """
    if instance.slot:
        instance.slot.is_available = False
        instance.slot.reserved_by = instance.contract
        instance.slot.save()


@receiver(pre_delete, sender=ContractAsset)
def release_slot_on_delete(sender, instance, **kwargs):
    """
    Освобождает слот при удалении привязки актива к договору
    """
    if instance.slot:
        instance.slot.is_available = True
        instance.slot.reserved_by = None
        instance.slot.save()


@receiver(post_save, sender=Payment)
def update_contract_status_on_payment(sender, instance, created, **kwargs):
    """
    Обновляет статус договора при подтверждении платежа
    """
    if instance.is_confirmed:
        contract = instance.contract
        paid_amount = contract.payments.filter(is_confirmed=True).aggregate(
            Sum('amount')
        )['amount__sum'] or 0

        # Если оплачена вся сумма - отмечаем договор как полностью оплаченный
        if paid_amount >= contract.total_amount:
            contract.is_fully_paid = True
            contract.save()


@receiver(post_save, sender=Deal)
def create_initial_task_for_new_deal(sender, instance, created, **kwargs):
    """
    Создает начальную задачу при создании новой сделки
    """
    if created:
        DealTask.objects.create(
            deal=instance,
            title=f"Первичный контакт с {instance.client}",
            description=f"Связаться с клиентом {instance.client} для уточнения деталей",
            due_date=timezone.now().date() + timezone.timedelta(days=3),
            priority=DealTask.Priority.MEDIUM
        )


@receiver(pre_save, sender=Deal)
def update_deal_status(sender, instance, **kwargs):
    """
    Автоматически обновляет дату закрытия при изменении статуса сделки
    """
    if instance.status in [Deal.Status.WON, Deal.Status.LOST] and not instance.closed_at:
        instance.closed_at = timezone.now()


@receiver(post_save, sender=AvailabilitySlot)
def validate_slot_overlap(sender, instance, created, **kwargs):
    """
    Проверяет отсутствие пересечений слотов для одного актива
    """
    if created:
        overlapping_slots = AvailabilitySlot.objects.filter(
            asset=instance.asset,
            start_date__lt=instance.end_date,
            end_date__gt=instance.start_date
        ).exclude(pk=instance.pk)

        if overlapping_slots.exists():
            raise ValidationError("Слот пересекается с существующим периодом")


@receiver(pre_save, sender=DealTask)
def set_task_completion_date(sender, instance, **kwargs):
    """
    Устанавливает дату выполнения при завершении задачи
    """
    if instance.is_done and not instance.completed_at:
        instance.completed_at = timezone.now()


def register_signals():
    """Явная регистрация сигналов (альтернатива декораторам)"""
    pass  # Все сигналы уже зарегистрированы через декораторы @receiver

# Альтернативный вариант регистрации без декораторов:
# pre_save.connect(update_contract_total_amount, sender=Contract)
# post_save.connect(update_slot_availability, sender=ContractAsset)
# pre_delete.connect(release_slot_on_delete, sender=ContractAsset)
# и т.д.