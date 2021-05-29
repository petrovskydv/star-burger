from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from geopy import distance

from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from foodcartapp.utils import fetch_coordinates
from star_burger.settings import YANDEX_GEOCODER_TOKEN


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:
        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.fetch_with_order_cost().all()
    menu = RestaurantMenuItem.objects.filter(availability=True).select_related('restaurant').select_related('product')
    menu_items = {}
    for menu_item in menu:
        menu_items.setdefault(menu_item.product.id, list()).append(menu_item.restaurant)

    for order in orders:
        order_items = order.order_items.all().values('product')
        order_items_restaurants = [menu_items[order_item['product']] for order_item in order_items]
        order_restaurants = set.intersection(
            *[set(order_item_restaurants) for order_item_restaurants in order_items_restaurants])

        order_coordinates = fetch_coordinates(YANDEX_GEOCODER_TOKEN, order.address)
        order_restaurants_coordinates = []
        for order_restaurant in order_restaurants:
            restaurant_coordinates = fetch_coordinates(YANDEX_GEOCODER_TOKEN, order_restaurant.address)
            restaurant_distance = distance.distance(order_coordinates, restaurant_coordinates).km
            order_restaurants_coordinates.append([order_restaurant, round(restaurant_distance, 3)])

        order.order_restaurants = sorted(order_restaurants_coordinates, key=lambda restaurant: restaurant[1])

    return render(
        request,
        template_name='order_items.html',
        context={'order_items': orders}
    )
