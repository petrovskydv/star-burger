# Generated by Django 3.2 on 2021-05-23 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_auto_20210523_1340'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.CharField(choices=[('cash', 'Наличными'), ('on_website', 'Оплата на сайте')], default='cash', max_length=20, verbose_name='Способ оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('processed', 'Обработанный'), ('not_processed', 'Необработанный')], default='not_processed', max_length=20, verbose_name='статус'),
        ),
    ]
