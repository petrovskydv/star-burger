from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

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


@api_view(['POST'])
def register_order(request):
    try:
        details_order = request.data

        if isinstance(details_order['products'], list):
            if len(details_order['products']) == 0:
                content = {'error': 'список продуктов пуст'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            content = {'error': 'вместо списка продуктов получен другой тип данных'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if not details_order['products']:
            content = {'error': 'вместо списка продуктов передан NULL'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            firstname=details_order['firstname'],
            lastname=details_order['lastname'],
            address=details_order['address'],
            phone_number=details_order['phonenumber'],
        )
        for product in details_order['products']:
            order_item = OrderItem.objects.create(
                product=Product.objects.get(pk=product['product']),
                order=order,
                quantity=product['quantity']
            )

        return JsonResponse({})
    except ValueError:
        return JsonResponse({
            'error': 'error',
        })
    except KeyError as e:
        content = {'error': repr(e)}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    except Product.DoesNotExist as e:
        content = {'error': 'продукт не найден'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)
