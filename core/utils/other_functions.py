import json

from transliterate import translit

from core.utils.db_api.api_sqlite import get_information


async def get_translated_city(name_city: str):
    with open('core/utils/russian-cities.json', 'r', encoding='utf-8') as f:
        russian_cities = json.load(f)
        for city in russian_cities:
            city_name = city['name'].lower().replace('ё', 'е')
            if city_name == name_city:
                translated_city = translit(city_name, reversed=True)
                return translated_city
        return None


async def transform_markets(markets):
    string_all_markets = '<b>🛒Магазины:</b>\n\n'
    count = 1
    for market in markets:
        string_all_markets += str(count) + '. ' + market['name'].capitalize() + "\n"
        count += 1
    string_all_markets += '\nДля выбора магазина напишите его название или номер в списке!'
    return string_all_markets


async def get_market_id(markets, name_market):
    if name_market.isdigit():
        if 1 <= int(name_market) <= len(markets):
            return markets[int(name_market) - 1]['uuid']
    else:
        for market in markets:
            if market['name'].lower() == name_market.lower():
                return market['uuid']
    return None


async def create_product_info(product_info) -> str:
    discount = f'{product_info["discount"]}%' if isinstance(product_info['discount'], int) else product_info[
        "discount"]
    price_before = f'<s>{product_info["priceBefore"]}</s>' if product_info[
                                                                  'priceBefore'] != 'Неизвестна' else '<code>Неизвестна</code>'
    weight = f'{product_info["weight"]}{product_info["unitOfMeasurement"]}' if isinstance(product_info['weight'],
                                                                                          float) else 'Неизвестен'
    info = f"Продукт: <code>{product_info['name']}</code>" \
           f"\nВес: <code>{weight}</code>" \
           f"\nЦена до акции: {price_before}" \
           f"\nЦена по акции: <code>{product_info['priceAfter']}</code>" \
           f"\nСкидка: <code>{discount}</code>" \
           f"\nСрок акции: <code>{product_info['date']}</code>" \
           f"\nМагазин: <code>{product_info['shopName']}</code>"
    return info


async def create_user_info(user_id):
    user_info = get_information('users_info', user_id=user_id)
    user_city = get_information('users_cities', user_id=user_id)
    info = f'<b>👤Профиль:</b>\n\n' \
           f'💎Логин: <code>{user_info["user_login"]}</code>\n' \
           f'🕐Регистрация: <code>{user_info["registration_date"]}</code>\n' \
           f'🏢Город: <code>{user_city["name_city"]}</code>\n' \
           f'⭐Избранных товаров: <code>{user_info["number_selected_products"]} из 3</code>'
    return info


async def create_wth_discount_info(user_id, product_name):
    favourites_products = get_information('users_favorites', user_id=user_id)['favourites_products']
    text = f'❕<b>На данный продукт нет скидок</b>\n\n' \
           f'Название: <code>{product_name}</code>\n\n'
    flag = True
    if favourites_products is not None:
        favourites_products = favourites_products.split(';')
        if len(favourites_products) < 3:
            if product_name in favourites_products:
                text += 'Данный товар уже находится в "⭐Избранном", ' \
                        'когда товар появится по акции, вам придёт уведомление!'
                flag = False
            else:
                text += f'Вы можете добавить его в "⭐Избранное",' \
                        f' когда товар появится по акции, вам придёт уведомление!'
        else:
            text += 'У вас уже добавлено максимальное кол-во товаров в "⭐Избранное"'
            flag = False
    else:
        text += f'Вы можете добавить его в "⭐Избранное",' \
                f' когда товар появится по акции, вам придёт уведомление!'
    return text, flag


async def clear_firstname(firstname: str) -> str:
    if "<" in firstname:
        firstname = firstname.replace("<", "*")
    if ">" in firstname:
        firstname = firstname.replace(">", "*")
    return firstname
