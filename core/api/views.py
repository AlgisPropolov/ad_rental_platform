from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from core.models import Asset, Contract, AvailabilitySlot, Deal, Payment  # Добавлен импорт Deal
from .serializers import (
    AssetSerializer,
    ContractSerializer,
    DealSerializer,
    PaymentSerializer,
    AvailabilitySlotSerializer
)


class AssetViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы с рекламными активами.
    Включает кастомный метод для получения слотов доступности.
    """
    queryset = Asset.objects.select_related('zone').prefetch_related('tags')
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Фильтрация по параметрам запроса
        asset_type = self.request.query_params.get('type')
        zone = self.request.query_params.get('zone')
        is_active = self.request.query_params.get('is_active')

        if asset_type:
            queryset = queryset.filter(asset_type=asset_type)
        if zone:
            queryset = queryset.filter(zone=zone)
        if is_active:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset

    @action(detail=True, methods=['get'], url_path='slots')
    def slots(self, request, pk=None):
        """Получение слотов доступности для актива"""
        asset = self.get_object()

        # Параметры фильтрации из запроса
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        only_available = request.query_params.get('only_available', 'true').lower() == 'true'

        # Базовый запрос
        slots = asset.availability_slots.all()

        # Применяем фильтры
        if start_date:
            slots = slots.filter(end_date__gte=start_date)
        if end_date:
            slots = slots.filter(start_date__lte=end_date)
        if only_available:
            slots = slots.filter(is_available=True)

        # Сериализация и возврат данных
        serializer = AvailabilitySlotSerializer(slots, many=True)
        return Response({
            'asset_id': asset.id,
            'asset_name': asset.name,
            'slots': serializer.data
        })


class ContractViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы с договорами.
    Включает оптимизированные запросы к БД.
    """
    queryset = Contract.objects.select_related('client', 'deal').prefetch_related('assets')
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Фильтрация по статусу
        is_active = self.request.query_params.get('is_active')
        if is_active:
            if is_active.lower() == 'true':
                queryset = queryset.filter(
                    is_active=True,
                    start_date__lte=timezone.now().date(),
                    end_date__gte=timezone.now().date()
                )
            else:
                queryset = queryset.filter(
                    Q(is_active=False) |
                    Q(end_date__lt=timezone.now().date())
                )

        return queryset


@api_view(['GET'])
def asset_slots(request, asset_id):
    """
    Альтернативная реализация получения слотов через function-based view.
    Возвращает слоты доступности для указанного актива.
    """
    asset = get_object_or_404(Asset, id=asset_id)

    # Параметры фильтрации
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    only_available = request.query_params.get('only_available', 'true').lower() == 'true'

    # Формируем запрос
    slots = AvailabilitySlot.objects.filter(asset=asset)

    if start_date:
        slots = slots.filter(end_date__gte=start_date)
    if end_date:
        slots = slots.filter(start_date__lte=end_date)
    if only_available:
        slots = slots.filter(is_available=True)

    # Сериализация данных
    serializer = AvailabilitySlotSerializer(slots, many=True)

    return Response({
        'asset': {
            'id': asset.id,
            'name': asset.name,
            'type': asset.get_asset_type_display()
        },
        'slots': serializer.data,
        'count': slots.count()
    })


# Дополнительные ViewSets (Deal, Payment и т.д.)
class DealViewSet(viewsets.ModelViewSet):
    queryset = Deal.objects.select_related('client', 'manager')
    serializer_class = DealSerializer
    permission_classes = [IsAuthenticated]


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('contract')
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]