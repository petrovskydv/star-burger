from contextlib import suppress

import requests
from requests import HTTPError

from location.models import Place
from star_burger.settings import YANDEX_GEOCODER_TOKEN


def fetch_coordinates(place):
    location, created = Place.objects.get_or_create(
        address=place
    )
    if created:
        with suppress(HTTPError):
            base_url = "https://geocode-maps.yandex.ru/1.x"
            params = {"geocode": place, "apikey": YANDEX_GEOCODER_TOKEN, "format": "json"}
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            found_places = response.json()['response']['GeoObjectCollection']['featureMember']
            if not found_places:
                return None, None
            most_relevant = found_places[0]
            location.longitude, location.latitude = most_relevant['GeoObject']['Point']['pos'].split(" ")
            location.save()

    return location.longitude, location.latitude


def find_coordinates(address, places):
    for place in places:
        if place['address'] == address:
            return place['longitude'], place['latitude']
    fetch_coordinates(address)


def fetch_order_restaurants(order_items_id, product_to_restaurants):
    order_items_restaurants = [product_to_restaurants[order_item_id] for order_item_id in order_items_id]
    order_restaurants = set.intersection(
        *[set(order_item_restaurants) for order_item_restaurants in order_items_restaurants])
    return order_restaurants
