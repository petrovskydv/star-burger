from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import product_list_api, banners_list_api, register_order

app_name = "foodcartapp"

urlpatterns = [
    path('products/', product_list_api),
    path('banners/', banners_list_api),
    path('order/', csrf_exempt(register_order)),
]
