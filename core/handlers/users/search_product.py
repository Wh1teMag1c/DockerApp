from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

from core.filters.all_filters import ChatTypeFilter
from core.keyboards.default.user_keyboard import main_menu, back_button
from core.keyboards.inline.all_inline import view_products_menu, adding_to_favourites
from core.states.all_states import MainMenu, SearchProduct
from core.utils.db_api.api_sqlite import get_information, update_information
from core.utils.other_functions import transform_markets, get_market_id, create_product_info, \
    create_wth_discount_info
from core.utils.parser_edadeal.parser_requests import get_supermarkets, get_products

router = Router()


@router.message(ChatTypeFilter(chat_type='private'), SearchProduct.write_name_product)
async def get_name_product(message: Message, state: FSMContext):
    product_name = message.text.title()
    await state.set_state(MainMenu.await_page)
    await message.answer(text='Отлично, теперь ожидайте, идёт поиск доступных магазинов...')
    city_info = get_information('users_cities', user_id=message.from_user.id)
    markets = await get_supermarkets(city_info['geo_id_city'], city_info['lat_city'], city_info['lng_city'])
    if len(markets) != 0:
        list_markets = await transform_markets(markets)
        await message.answer(text=list_markets, reply_markup=back_button)
        await state.update_data(product_name=product_name, markets=markets, city_info=city_info)
        await state.set_state(SearchProduct.choose_market)
    else:
        await message.answer(text="<b>🛠Технические работы🛠</b>\n\n"
                                  "Повторите попытку немного позже, если проблемы не решится, измените город поиска!")
        await message.answer(text='<b>↪Возвращаемся в главное меню...</b>',
                             reply_markup=main_menu)
        await state.clear()
        await state.set_state(MainMenu.main_page)


@router.message(ChatTypeFilter(chat_type='private'), SearchProduct.choose_market)
async def choose_name_market(message: Message, state: FSMContext):
    market_name = message.text
    await state.set_state(MainMenu.await_page)
    data = await state.get_data()
    markets = data['markets']
    market_id = await get_market_id(markets, market_name)
    if market_id is not None:
        await message.answer(
            text='Супер, теперь ожидайте, идёт поиск товара...')
        products_list = await get_products(data['product_name'], data['city_info']['geo_id_city'],
                                           data['city_info']['lat_city'], data['city_info']['lng_city'],
                                           market_id)
        if len(products_list) > 0:
            product_info = await create_product_info(products_list[0])
            message = await message.answer_photo(photo=products_list[0]['photo'],
                                                 caption=product_info,
                                                 reply_markup=await view_products_menu(1, len(products_list)))
            await state.update_data(products_list=products_list, current_page=1,
                                    message_id_products=message.message_id)
        else:
            info_wth_discount, flag = await create_wth_discount_info(message.from_user.id, data['product_name'])
            message = await message.answer(
                text=info_wth_discount,
                reply_markup=await adding_to_favourites(flag))
            await state.update_data(message_id_products=message.message_id)
        await state.set_state(SearchProduct.view_products)
    else:
        await message.answer(
            text='<b>❗Ошибка</b>\n\nВ списке нет данного магазина!\nПопробуйте ещё раз.')
        await state.set_state(SearchProduct.choose_market)


@router.callback_query(SearchProduct.view_products, F.data == 'next_page')
async def open_next_page(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        products_list = data['products_list']
        current_page = data['current_page']
        if current_page < len(products_list):
            product_info = await create_product_info(products_list[current_page])
            photo = InputMediaPhoto(media=products_list[current_page]['photo'], caption=product_info)
            await callback.message.edit_media(media=photo,
                                              reply_markup=await view_products_menu(current_page + 1,
                                                                                    len(products_list)))
            await state.update_data(current_page=current_page + 1)
    except:
        pass


@router.callback_query(SearchProduct.view_products, F.data == 'back_page')
async def open_back_page(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        products_list = data['products_list']
        current_page = data['current_page']
        if current_page > 1:
            product_info = await create_product_info(products_list[current_page - 2])
            photo = InputMediaPhoto(media=products_list[current_page - 2]['photo'], caption=product_info)
            await callback.message.edit_media(media=photo,
                                              reply_markup=await view_products_menu(current_page - 1,
                                                                                    len(products_list)))
            await state.update_data(current_page=current_page - 1)
    except:
        pass


@router.callback_query(SearchProduct.view_products, F.data == 'close_menu_products')
async def close_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text='<b>↪Возвращаемся в главное меню...</b>',
                                  reply_markup=main_menu)
    await state.clear()
    await state.set_state(MainMenu.main_page)


@router.callback_query(SearchProduct.view_products, F.data == 'add_favorite')
async def add_favourite_product(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text='<b>✅Продукт успешно добавлен в "⭐Избранное"</b>',
                                  reply_markup=main_menu)
    data = await state.get_data()
    product_name = data['product_name']
    favourites_products = get_information('users_favorites', user_id=callback.from_user.id)['favourites_products']
    favourites_products = [] if favourites_products is None else favourites_products.split(';')
    favourites_products.append(product_name)
    update_information('users_favorites', user_id=callback.from_user.id,
                       favourites_products=';'.join(favourites_products))
    update_information('users_info', user_id=callback.from_user.id, number_selected_products=len(favourites_products))
    await state.clear()
    await state.set_state(MainMenu.main_page)
