from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField
from rest_framework.serializers import ModelSerializer

from foodcartapp.models import OrderItem, Order


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            'quantity',
            'product'
        )


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True, write_only=True, allow_empty=False)
    phonenumber = PhoneNumberField(source='phone_number')
    id = IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'firstname',
            'lastname',
            'phonenumber',
            'address',
            'products',
        )
