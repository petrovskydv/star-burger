import requests
from requests import HTTPError

from location.models import Place
from star_burger.settings import YANDEX_GEOCODER_TOKEN


def fetch_coordinates(place):
    location, created = Place.objects.get_or_create(
        address=place
    )
    if created:
        try:
            base_url = "https://geocode-maps.yandex.ru/1.x"
            params = {"geocode": place, "apikey": YANDEX_GEOCODER_TOKEN, "format": "json"}
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            found_places = response.json()['response']['GeoObjectCollection']['featureMember']
            if len(found_places) == 0:
                return
            most_relevant = found_places[0]
            location.longitude, location.latitude = most_relevant['GeoObject']['Point']['pos'].split(" ")
            location.save()
        except HTTPError:
            pass
    return location.longitude, location.latitude
