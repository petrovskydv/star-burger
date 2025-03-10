from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Sum, F
from django.utils import timezone
from geopy import distance
from phonenumber_field.modelfields import PhoneNumberField

from foodcartapp.utils import find_coordinates


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
                .filter(availability=True)
                .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def fetch_with_order_cost(self):
        return self.annotate(product_cost=Sum(F('order_items__quantity') * F('order_items__price')))


class Order(models.Model):
    order_choices = [
        ('processed', 'Обработанный'),
        ('not_processed', 'Необработанный'),
    ]
    pay_choices = [
        ('not_defined', 'Не определен'),
        ('cash', 'Наличными'),
        ('on_website', 'Оплата на сайте'),
    ]

    status = models.CharField('статус', max_length=20, choices=order_choices, default='not_processed', db_index=True)
    payment = models.CharField('Способ оплаты', max_length=20, choices=pay_choices, default='not_defined',
                               db_index=True)
    firstname = models.CharField('Имя', max_length=50)
    lastname = models.CharField('Фамилия', max_length=50)
    address = models.CharField('Адрес', max_length=50)
    phone_number = PhoneNumberField('Мобильный номер', max_length=50, db_index=True)
    comment = models.TextField('комментарий', max_length=200, blank=True)
    registrated = models.DateTimeField('зарегистрирован', default=timezone.now, db_index=True)
    called = models.DateTimeField('дата звонка', blank=True, null=True, db_index=True)
    delivered = models.DateTimeField('доставлен', blank=True, null=True, db_index=True)
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name="ресторан",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.address}'

    def fetch_restaurants_distance(self, order_restaurants, places):
        order_coordinates = find_coordinates(self.address, places)
        if not order_coordinates[0]:
            return [['Нет координат заказа', '']]

        order_restaurants_coordinates = []
        for order_restaurant in order_restaurants:
            restaurant_coordinates = find_coordinates(order_restaurant.address, places)
            if not restaurant_coordinates[0]:
                continue
            restaurant_distance = distance.distance(order_coordinates, restaurant_coordinates).km
            order_restaurants_coordinates.append([order_restaurant, round(restaurant_distance, 3)])

        if not order_restaurants_coordinates:
            return [['Нет удалось определить расстояние', '']]
        return sorted(order_restaurants_coordinates, key=lambda restaurant: restaurant[1])


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='order_items',
        verbose_name='заказ',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name='товар',
    )
    quantity = models.IntegerField(
        'количество',
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    price = models.DecimalField(
        'цена',
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'
        unique_together = [
            ['order', 'product']
        ]

    def __str__(self):
        return f'{self.product.name} - {self.order.firstname} {self.order.lastname} {self.order.address}'
