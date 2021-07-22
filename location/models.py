from django.db import models


class Place(models.Model):
    address = models.CharField('адрес', max_length=100, unique=True)
    latitude = models.FloatField('широта', blank=True, null=True)
    longitude = models.FloatField('долгота', blank=True, null=True)
    received_at = models.DateTimeField('дата получения координат', auto_now=True)

    class Meta:
        verbose_name = 'место'
        verbose_name_plural = 'места'

    def __str__(self):
        return self.address
