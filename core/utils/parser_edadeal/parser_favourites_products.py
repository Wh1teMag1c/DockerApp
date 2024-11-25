import asyncio

import aiohttp

from core.utils.db_api.api_sqlite import get_all_information, get_information
from core.utils.parser_edadeal.parser_requests import get_count_discounts
from loader import bot


async def parse_products(session, user_id, geo_id_ciy, lat_city, lng_city, product_name):
    count_discounts = await get_count_discounts(session, product_name, geo_id_ciy, lat_city, lng_city)
    if count_discounts > 0:
        await bot.send_message(user_id, text=f'<b>⭐Продукт из Избранных товаров появился по скидке</b>\n\n'
                                             f'Название: <code>{product_name}</code>\n'
                                             f'Найдено акций: <code>{count_discounts}</code>\n\n'
                                             f'Чтобы уточнить все подробности акции, воспользуйтесь 🔍 Поиском')


async def create_tasks():
    async with aiohttp.ClientSession() as session:
        users_favourites_products = get_all_information('users_favorites')
        tasks = []
        for user_favourites_products in users_favourites_products:
            user = get_information('users_info', user_id=user_favourites_products['user_id'])
            user_city = get_information('users_cities', user_id=user_favourites_products['user_id'])
            if user_favourites_products['favourites_products'] is not None:
                for favourite_product in user_favourites_products['favourites_products'].split(';'):
                    tasks.append(asyncio.create_task(
                        parse_products(session, user['user_id'], user_city['geo_id_city'], user_city['lat_city'],
                                       user_city['lng_city'], favourite_product)))
        await asyncio.gather(*tasks)
        await session.close()
