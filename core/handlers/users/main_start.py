from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile

from core.filters.all_filters import ChatTypeFilter
from core.keyboards.default.user_keyboard import main_menu
from core.states.all_states import Registration, MainMenu, SearchProduct
from core.utils.db_api.api_sqlite import get_information, update_information
from core.utils.other_functions import clear_firstname

router = Router()


@router.message(CommandStart(), ChatTypeFilter(chat_type='private'))
async def bot_start(message: Message, state: FSMContext, bot: Bot):
    user_name = await clear_firstname(message.from_user.first_name)
    user_login = message.from_user.username
    get_user_id = get_information('users_info', user_id=message.from_user.id)
    photo = FSInputFile(f'core/images/photo_1.png')
    if get_user_id is None:
        await message.answer_photo(photo,
                                   f"👋<b>Привет, <a href='tg://user?id={message.from_user.id}'>{user_name}</a>"
                                   f"\n\nДанный бот предназначен для поиска акций на товары"
                                   f" в продуктовых магазинах!</b>")
        await message.answer(text='<b>📝Регистрация</b>\n\nДля продолжения введите свой город!\nПример: Москва')
        await state.set_state(Registration.write_city)
    else:
        if user_name != get_user_id['user_name']:
            update_information('users_info', get_user_id['user_id'], user_name=user_name)
        if user_login is not None:
            if user_login != get_user_id['user_login']:
                update_information('users_info', get_user_id['user_id'], user_login=user_login)
        await message.answer_photo(photo,
                                   f"👋<b>Привет, <a href='tg://user?id={message.from_user.id}'>{user_name}</a>"
                                   f"\n\nДанный бот предназначен для поиска акций на товары"
                                   f" в продуктовых магазинах!</b>",
                                   reply_markup=main_menu)
        current_state = await state.get_state()
        if current_state == SearchProduct.view_products:
            data = await state.get_data()
            await bot.delete_message(message.from_user.id, data['message_id_products'])
            await state.update_data(message_id_products=0)
        await state.set_state(MainMenu.main_page)
