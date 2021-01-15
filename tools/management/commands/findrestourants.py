from django.core.management.base import BaseCommand

import json
import requests
import colored
from colored import stylize
from pathlib import Path
import os

LANG = "ru_RU"
MAX_RESULTS = 500
LOCATION = "Россия"
FIXTURE_PATH = Path(__file__).parents[3]


def find_restaurants(restaurant, data=None, skip=0):
    if data is None:
        data = []

    query = f'https://search-maps.yandex.ru/v1/' \
            f'?apikey={os.environ["YANDEX_APIKEY"]}' \
            f'&text={restaurant},{LOCATION}' \
            f'&lang={LANG}' \
            f'&results={MAX_RESULTS}' \
            f'&skip={skip}'

    response = requests.get(query)
    result = [i for i in response.json()["features"]]
    data += result

    if len(result) == MAX_RESULTS:
        skip += MAX_RESULTS
        return find_restaurants(restaurant=restaurant, data=data, skip=skip)
    else:
        print(stylize(f"[ '{restaurant}' restaurant data collected, number of found: {len(data)} ]",
                      colored.fg("green_yellow")))
        return data


def company_check(name):
    pass


def packer(data):
    packed_data = []

    for restaurant in data:
        meta = restaurant["properties"]["CompanyMetaData"]
        yandex_id = meta["id"]
        company = restaurant["properties"]["name"]

        address = meta["address"].split(",")
        region = address[1].strip()
        city = address[2].strip()

        fixture_template = {
            "model": "restaurant.restaurant",
            "pk": "null",
            "fields": {
                "yandex_id": yandex_id,
                "company": company,
                "region": region,
                "city": city
            }
        }

        packed_data.append(fixture_template)

    return packed_data


def fixture_writer(packed_data, file):
    with open(f"{FIXTURE_PATH}/fixtures/{file}.json", "w") as f:
        f.write(json.dumps(packed_data, ensure_ascii=False, indent=4))


class Command(BaseCommand):
    help = "Find restaurant data on Yandex.API and create fixture"

    def add_arguments(self, parser):
        parser.add_argument('restaurant_name', type=str, help='Restaurant name')
        parser.add_argument('fixture_name', type=str, help='Fixture output file name')

    def handle(self, *args, **kwargs):
        restaurant_name = kwargs['restaurant_name']
        fixture_name = kwargs["fixture_name"]
        if restaurant_name is None:
            print(stylize("[ Need a restaurant name, example: 'Бургер Кинг' ]", colored.fg("red")))
        if fixture_name is None:
            print(stylize("[ Need a fixture output file name, example: 'burger' ]", colored.fg("red")))
        if restaurant_name and fixture_name:
            print(stylize("[ Processing ]", colored.fg("green_yellow")))
            raw_data = find_restaurants(restaurant_name)
            packed_data = packer(raw_data)
            fixture_writer(packed_data, fixture_name)
