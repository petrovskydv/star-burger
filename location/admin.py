from django.contrib import admin

from location.models import Place


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    pass
