from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models import (
    Client, Asset, AvailabilitySlot,
    Deal, Contract, Payment, DealTask, Tag, ContractAsset
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = fields


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color']
        read_only_fields = ['id']


class ClientSerializer(serializers.ModelSerializer):
    manager = UserSerializer(read_only=True)
    manager_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='manager',
        write_only=True,
        required=False
    )

    class Meta:
        model = Client
        fields = [
            'id', 'name', 'inn', 'contact_person', 'phone', 'email',
            'is_vip', 'is_active', 'notes', 'manager', 'manager_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_inn(self, value):
        if value and len(value) not in (10, 12):
            raise ValidationError("ИНН должен содержать 10 или 12 цифр")
        return value


class AssetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    current_contract = serializers.SerializerMethodField()
    zone_display = serializers.CharField(source='get_zone_display', read_only=True)
    asset_type_display = serializers.CharField(source='get_asset_type_display', read_only=True)

    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'asset_type', 'asset_type_display', 'zone', 'zone_display',
            'location', 'daily_rate', 'is_active', 'tags', 'current_contract',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'current_contract']

    def get_current_contract(self, obj):
        contract = obj.current_contract()
        if contract:
            return ContractListSerializer(contract).data
        return None


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    asset = serializers.PrimaryKeyRelatedField(queryset=Asset.objects.all())
    reserved_by = serializers.PrimaryKeyRelatedField(
        queryset=Contract.objects.all(),
        required=False,
        allow_null=True
    )
    status = serializers.SerializerMethodField()

    class Meta:
        model = AvailabilitySlot
        fields = [
            'id', 'asset', 'start_date', 'end_date',
            'is_available', 'reserved_by', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']

    def get_status(self, obj):
        return "available" if obj.is_available else "reserved"

    def validate(self, data):
        if data['end_date'] < data['start_date']:
            raise ValidationError("Дата окончания должна быть позже даты начала")

        overlapping = AvailabilitySlot.objects.filter(
            asset=data['asset'],
            start_date__lt=data['end_date'],
            end_date__gt=data['start_date']
        ).exclude(id=self.instance.id if self.instance else None)

        if overlapping.exists():
            raise ValidationError("Период пересекается с существующим слотом")

        return data


class DealListSerializer(serializers.ModelSerializer):
    client = serializers.StringRelatedField()
    manager = serializers.StringRelatedField()
    status_display = serializers.CharField(source='get_status_display')

    class Meta:
        model = Deal
        fields = [
            'id', 'title', 'client', 'manager', 'status',
            'status_display', 'expected_amount', 'probability',
            'created_at'
        ]


class DealSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        source='client',
        write_only=True
    )
    manager = UserSerializer(read_only=True)
    manager_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='manager',
        write_only=True
    )

    class Meta:
        model = Deal
        fields = [
            'id', 'title', 'client', 'client_id', 'manager', 'manager_id',
            'status', 'expected_amount', 'probability', 'closed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        if data.get('status') in [Deal.Status.WON, Deal.Status.LOST] and not data.get('closed_at'):
            data['closed_at'] = timezone.now()
        return data


class ContractAssetSerializer(serializers.ModelSerializer):
    asset = AssetSerializer(read_only=True)
    asset_id = serializers.PrimaryKeyRelatedField(
        queryset=Asset.objects.all(),
        source='asset',
        write_only=True
    )
    slot = AvailabilitySlotSerializer(read_only=True)
    slot_id = serializers.PrimaryKeyRelatedField(
        queryset=AvailabilitySlot.objects.all(),
        source='slot',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = ContractAsset
        fields = [
            'id', 'contract', 'asset', 'asset_id', 'slot', 'slot_id',
            'price', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ContractListSerializer(serializers.ModelSerializer):
    client = serializers.StringRelatedField()
    status = serializers.SerializerMethodField()
    payment_type_display = serializers.CharField(source='get_payment_type_display')

    class Meta:
        model = Contract
        fields = [
            'id', 'number', 'client', 'start_date', 'end_date',
            'total_amount', 'payment_type', 'payment_type_display',
            'signed', 'status'
        ]

    def get_status(self, obj):
        today = timezone.now().date()
        if obj.end_date < today:
            return 'expired'
        elif obj.start_date > today:
            return 'upcoming'
        return 'active'


class ContractSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        source='client',
        write_only=True
    )
    deal = DealSerializer(read_only=True)
    deal_id = serializers.PrimaryKeyRelatedField(
        queryset=Deal.objects.all(),
        source='deal',
        write_only=True,
        required=False,
        allow_null=True
    )
    assets = ContractAssetSerializer(many=True, read_only=True)
    document_url = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = [
            'id', 'number', 'client', 'client_id', 'deal', 'deal_id',
            'start_date', 'end_date', 'total_amount', 'payment_type',
            'signed', 'signed_date', 'is_active', 'document', 'document_url',
            'assets', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_amount', 'assets']

    def get_document_url(self, obj):
        if obj.document:
            return self.context['request'].build_absolute_uri(obj.document.url)
        return None

    def validate(self, data):
        if data['end_date'] < data['start_date']:
            raise ValidationError("Дата окончания договора должна быть позже даты начала")
        return data


class PaymentSerializer(serializers.ModelSerializer):
    contract = ContractListSerializer(read_only=True)
    contract_id = serializers.PrimaryKeyRelatedField(
        queryset=Contract.objects.all(),
        source='contract',
        write_only=True
    )
    payment_method_display = serializers.CharField(source='get_payment_method_display')
    status_display = serializers.CharField(source='get_status_display')
    receipt_url = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'contract', 'contract_id', 'amount', 'date',
            'payment_method', 'payment_method_display', 'status',
            'status_display', 'is_confirmed', 'confirmation_date',
            'transaction_id', 'receipt', 'receipt_url', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'confirmation_date',
            'payment_method_display', 'status_display'
        ]

    def get_receipt_url(self, obj):
        if obj.receipt:
            return self.context['request'].build_absolute_uri(obj.receipt.url)
        return None

    def validate(self, data):
        if data['date'] > timezone.now().date():
            raise ValidationError("Дата платежа не может быть в будущем")
        return data


class DealTaskSerializer(serializers.ModelSerializer):
    deal = DealListSerializer(read_only=True)
    deal_id = serializers.PrimaryKeyRelatedField(
        queryset=Deal.objects.all(),
        source='deal',
        write_only=True
    )
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_to',
        write_only=True,
        required=False,
        allow_null=True
    )
    priority_display = serializers.CharField(source='get_priority_display')

    class Meta:
        model = DealTask
        fields = [
            'id', 'deal', 'deal_id', 'assigned_to', 'assigned_to_id',
            'title', 'description', 'is_done', 'due_date', 'priority',
            'priority_display', 'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'priority_display']

    def validate(self, data):
        if data.get('is_done') and not data.get('completed_at'):
            data['completed_at'] = timezone.now()
        return data