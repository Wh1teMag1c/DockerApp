from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from core.filters.all_filters import ChatTypeFilter
from core.keyboards.default.user_keyboard import main_menu, back_button
from core.keyboards.inline.all_inline import settings_button, view_favourite_products
from core.states.all_states import Registration, MainMenu, SearchProduct, ChangeCity
from core.utils.db_api.api_sqlite import add_user, get_information
from core.utils.other_functions import get_translated_city, create_user_info
from core.utils.parser_edadeal.parser_requests import get_city_info

router = Router()


@router.message(ChatTypeFilter(chat_type='private'), Registration.write_city)
async def registration_city(message: Message, state: FSMContext):
    user_city = message.text.lower().strip().replace(' ', '-').replace('ё', 'е')
    translated_city = await get_translated_city(user_city)
    if translated_city is not None:
        city_info = await get_city_info(translated_city)
        if city_info is not None:
            await message.answer(
                text=f'<b>✅Регистрация прошла успешно!</b>\n\nЧтобы продолжить выберите кнопку.',
                reply_markup=main_menu)
            user_name = message.from_user.full_name
            user_login = message.from_user.username
            add_user(message.from_user.id, user_login, user_name,
                     datetime.now().strftime("%d.%m.%Y %H:%M:%S"), user_city.title(), translated_city,
                     city_info['geoId'], city_info['center']['lat'], city_info['center']['lng'])
            await state.set_state(MainMenu.main_page)
        else:
            await message.answer(text=f'❗Данного города нет в нашей базе данных❗\nВведите другой город.')
    else:
        await message.answer(text=f'<b>❗Ошибка</b>\n\nДанного города не существует!\nПопробуйте ещё раз.')


@router.message(ChatTypeFilter(chat_type='private'), MainMenu.main_page, F.text == '👤 Профиль')
async def open_profile_page(message: Message):
    info = await create_user_info(message.from_user.id)
    await message.answer(text=info, reply_markup=settings_button)


@router.callback_query(MainMenu.main_page, F.data == 'edit_city')
async def edit_user_city(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        text='<b>⚙Изменение города</b>\n\nДля продолжения введите новый город!\nПример: Москва',
        reply_markup=back_button)
    await state.set_state(ChangeCity.write_new_city)


@router.message(ChatTypeFilter(chat_type='private'), MainMenu.main_page, F.text == '🔍 Поиск')
async def start_search(message: Message, state: FSMContext):
    await message.answer('<b>🔍 Поиск товаров</b>\n\n'
                         'Введите название нужного продукта!',
                         reply_markup=back_button)
    await state.set_state(SearchProduct.write_name_product)


@router.message(ChatTypeFilter(chat_type='private'), MainMenu.main_page, F.text == '⭐ Избранное')
async def get_favourite_products(message: Message):
    favourites_products = get_information('users_favorites', user_id=message.from_user.id)['favourites_products']
    favourites_products = [] if favourites_products is None or favourites_products == '' else favourites_products.split(
        ';')
    if len(favourites_products) == 0:
        await message.answer('<b>❕У вас нет товаров в "⭐Избранном"</b>\n\n'
                             'Если во время Поиска продукта на него не будет скидки,'
                             ' то Вы сможете добавить его в "⭐Избранное",'
                             ' и, когда товар появится по акции, вам придёт уведомление!')
    else:
        await message.answer('<b>⭐Избранные товары:</b>',
                             reply_markup=await view_favourite_products(favourites_products))


@router.message(ChatTypeFilter(chat_type='private'), F.text == '◀ Назад')
async def back_to_main_menu(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == SearchProduct.write_name_product or current_state == SearchProduct.choose_market:
        await message.answer(text='<b>↪Возвращаемся в главное меню...</b>',
                             reply_markup=main_menu)
        await state.set_state(MainMenu.main_page)
    elif current_state == ChangeCity.write_new_city:
        info = await create_user_info(message.from_user.id)
        await message.answer(
            text='<b>↪Возвращаемся в профиль...</b>',
            reply_markup=main_menu)
        await message.answer(
            text=info,
            reply_markup=settings_button)
        await state.set_state(MainMenu.main_page)
