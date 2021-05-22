# Generated by Django 3.2 on 2021-05-22 09:38

from django.db import migrations
from django.db.models import F, Subquery, OuterRef


def fill_price(apps, schema_editor):
    OrderItem = apps.get_model('foodcartapp', 'OrderItem')
    OrderItem.objects.update(
        price=Subquery(
            OrderItem.objects.filter(pk=OuterRef('pk')).values('product__price')[:1]
        )
    )


class Migration(migrations.Migration):
    dependencies = [
        ('foodcartapp', '0039_auto_20210522_1235'),
    ]

    operations = [
        migrations.RunPython(fill_price),
    ]
