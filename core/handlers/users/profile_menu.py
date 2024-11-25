from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.filters.all_filters import ChatTypeFilter
from core.keyboards.default.user_keyboard import main_menu, back_button
from core.keyboards.inline.all_inline import settings_button
from core.states.all_states import MainMenu, ChangeCity
from core.utils.db_api.api_sqlite import get_information, update_information
from core.utils.other_functions import get_translated_city, create_user_info
from core.utils.parser_edadeal.parser_requests import get_city_info

router = Router()


@router.message(ChatTypeFilter(chat_type='private'), ChangeCity.write_new_city)
async def get_new_city(message: Message, state: FSMContext):
    user_city = message.text.lower().strip().replace(' ', '-').replace('ё', 'е')
    translated_city = await get_translated_city(user_city)
    if translated_city is not None:
        city_info = await get_city_info(translated_city)
        if city_info is not None:
            update_information('users_cities', user_id=message.from_user.id, name_city=user_city.title(),
                               translate_user_city=translated_city, geo_id_city=city_info['geoId'],
                               lat_city=city_info['center']['lat'], lng_city=city_info['center']['lng'])
            info = await create_user_info(message.from_user.id)
            await message.answer(
                text=f'<b>✅Город успешно изменён!</b>',
                reply_markup=main_menu)
            await message.answer(
                text=info,
                reply_markup=settings_button)
            await state.set_state(MainMenu.main_page)
        else:
            await message.answer(text=f'❗Данного города нет в нашей базе данных❗\nВведите другой город.',
                                 reply_markup=back_button)
    else:
        await message.answer(
            text=f'<b>❗Ошибка</b>\n\nДанного города не существует!\nПопробуйте ещё раз.',
            reply_markup=back_button)
