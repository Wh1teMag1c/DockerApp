from datetime import datetime

import requests
from fake_useragent import UserAgent

user_agent = UserAgent()


def create_headers(city_id: int, city_lat: float, city_lng: float):
    headers = {
        'x-position-longitude': f'{city_lng}',
        'accept-language': 'ru',
        'x-platform': 'desktop',
        'x-locality-countrygeoid': '225',
        'x-locality-geoid': f'{city_id}',
        'sec-ch-ua-platform': '"Windows"',
        'x-app-id': 'edadeal',
        'x-position-latitude': f'{city_lat}',
        'User-Agent': f'{user_agent.chrome}',
        'Content-Type': 'application/json',
        'accept': 'application/json',
        'Referer': 'https://edadeal.ru/',
    }
    return headers


async def get_city_info(city: str):
    headers = {
        'User-Agent': f'{user_agent.chrome}'
    }
    params = {
        'id': f'{city}',
        'kind': 'locality',
    }
    try:
        response = requests.get('https://susanin.edadeal.ru/api/v1/search', params=params, headers=headers)
        return response.json()[0]
    except (KeyError, ValueError, requests.RequestException):
        return None


async def get_supermarkets(city_id: int, city_lat: float, city_lng: float):
    headers = create_headers(city_id, city_lat, city_lng)
    try:
        response = requests.get('https://search.edadeal.io/api/v4/location_info', headers=headers)
        all_markets = []
        supermarkets_uuid = response.json()['retailersByType'][0]['uuid']
        for retailer in response.json()['retailers']:
            if retailer['info']['typeUuid'] == supermarkets_uuid:
                all_markets.append({'name': retailer['info']['name'], 'uuid': retailer['uuid']})
        all_markets.append({'name': 'все магазины', 'uuid': 'all'})
        return all_markets
    except (KeyError, ValueError, requests.RequestException):
        return []


async def get_count_discounts(session, product_name, city_id, lat, lng):
    headers = create_headers(city_id, lat, lng)
    params = {
        'addContent': 'true',
        'allNanoOffers': 'true',
        'entities': '',
        'groupBy': 'sku_or_meta',
        'hasDiscount': 'true',
        'limit': '21',
        'offset': '0',
        'text': product_name,
    }
    url = 'https://search.edadeal.io/api/v4/search'
    try:
        response = await session.get(url, params=params, headers=headers)
        try:
            count_discounts = await response.json()
            return count_discounts.get('total', 0)
        except (KeyError, ValueError) as e:
            print(f"Ошибка при разборе JSON: {e}")
            return 0

    except requests.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return 0


async def get_products(product_name, city_id, lat, lng, shop_id):
    headers = create_headers(city_id, lat, lng)
    params = {
        'addContent': 'true',
        'allNanoOffers': 'true',
        'entities': '',
        'groupBy': 'sku_or_meta',
        'hasDiscount': 'true',
        'limit': '21',
        'offset': '0',
        'text': product_name,
    }
    if shop_id != 'all':
        params['retailerUuid'] = shop_id

    url = 'https://search.edadeal.io/api/v4/search'

    try:
        response = requests.get(url, params=params, headers=headers)
        try:
            products = response.json().get('items', [])

            all_products = []
            for product in products:
                if product.get('type') == 'sku':
                    product = product['items'][0]

                shop_name = product.get('partner', {}).get('name', 'Неизвестен')
                if shop_name is not None:
                    price_data = product.get('priceData', {})
                    price_before_value = price_data.get('old', {}).get('value', price_data.get('new', {}).get('to',
                                                                                                              'Неизвестна'))

                    if price_before_value is not None and isinstance(price_before_value, (int, float)):
                        price_before = f"{price_before_value / 100}₽"
                    else:
                        price_before = 'Неизвестна'

                    product_info = {
                        'shopName': shop_name,
                        'name': product.get('title', 'Неизвестен'),
                        'unitOfMeasurement': product.get('quantityUnit', 'Неизвестен'),
                        'weight': product.get('quantity', 'Неизвестен'),
                        'priceBefore': price_before,
                        'priceAfter': f"{price_data.get('new', {}).get('value', price_data.get('new', {}).get('from', 'Неизвестна')) / 100}₽",
                        'discount': product.get('discountPercent', 'Неизвестен'),
                        'date': f"До {datetime.utcfromtimestamp(product.get('dateEnd', 0) / 1000).strftime('%d.%m.%Y')}" if product.get(
                            'dateEnd') else 'Неизвестен',
                        'photo': product.get('imageUrl', ''),
                    }
                    all_products.append(product_info)

                if len(all_products) >= 10:
                    break

            return all_products

        except (KeyError, ValueError) as e:
            print(f"Ошибка при разборе JSON: {e}")
            return []

    except requests.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return []
