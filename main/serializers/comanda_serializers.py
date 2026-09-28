from rest_framework import serializers
from main.models.comanda import MenuItem, RestaurantTable, Comanda, ComandaItem, StaffToken


class MenuItemSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'image_url',
                  'category', 'category_display', 'subcategory', 'available',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class MenuItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'image_url', 'category', 'subcategory', 'available']


class RestaurantTableSerializer(serializers.ModelSerializer):
    open_comandas = serializers.SerializerMethodField()

    class Meta:
        model = RestaurantTable
        fields = ['id', 'identifier', 'capacity', 'open_comandas', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_open_comandas(self, obj):
        return obj.comandas.filter(status='OPEN').count()


class ComandaItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = ComandaItem
        fields = ['id', 'menu_item', 'item_name', 'item_price', 'quantity', 'notes', 'subtotal', 'added_at']
        read_only_fields = ['id', 'item_name', 'item_price', 'subtotal', 'added_at']

    def get_subtotal(self, obj):
        return float(obj.item_price * obj.quantity)


class ComandaItemCreateSerializer(serializers.Serializer):
    menu_item_id = serializers.IntegerField(required=False, allow_null=True)
    item_name    = serializers.CharField(max_length=200, required=False)
    item_price   = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    quantity     = serializers.IntegerField(min_value=1, default=1)
    notes        = serializers.CharField(max_length=300, required=False, allow_blank=True)

    def validate(self, data):
        if not data.get('menu_item_id') and not (data.get('item_name') and data.get('item_price') is not None):
            raise serializers.ValidationError('Informe menu_item_id ou item_name + item_price.')
        return data


class ComandaSerializer(serializers.ModelSerializer):
    items = ComandaItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Comanda
        fields = ['id', 'table', 'table_label', 'opened_by', 'status', 'status_display',
                  'notes', 'closed_at', 'created_at', 'total', 'items']
        read_only_fields = ['id', 'created_at', 'status_display', 'total']

    def get_total(self, obj):
        return float(sum(i.item_price * i.quantity for i in obj.items.all()))


class ComandaCreateSerializer(serializers.Serializer):
    table_id   = serializers.IntegerField(required=False, allow_null=True)
    table_label = serializers.CharField(max_length=50, required=False, allow_blank=True)
    opened_by  = serializers.CharField(max_length=150, default='Manager')
    notes      = serializers.CharField(required=False, allow_blank=True)


class StaffTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffToken
        fields = ['id', 'staff_name', 'token', 'active', 'created_at']
        read_only_fields = ['id', 'token', 'created_at']
