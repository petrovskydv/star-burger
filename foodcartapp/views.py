from django.http import JsonResponse
from django.templatetags.static import static
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from .models import Product, Order, OrderItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            'quantity',
            'product'
        )


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True)
    phonenumber = PhoneNumberField(source='phone_number')

    class Meta:
        model = Order
        fields = (
            'firstname',
            'lastname',
            'address',
            'products',
            'phonenumber',
        )

    def validate_products(self, value):
        if not value:
            raise ValidationError('Список продуктов пуст!')
        return value


@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    order = Order.objects.create(
        firstname=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        address=serializer.validated_data['address'],
        phone_number=serializer.validated_data['phone_number'],
    )

    order_items_fields = serializer.validated_data['products']
    order_items = [OrderItem(order=order, **fields) for fields in order_items_fields]
    OrderItem.objects.bulk_create(order_items)

    return Response({}, status=status.HTTP_200_OK)
