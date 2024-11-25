from aiogram import Router, F
from aiogram.types import CallbackQuery

from core.keyboards.inline.all_inline import view_favourite_products
from core.states.all_states import MainMenu
from core.utils.db_api.api_sqlite import get_information, update_information

router = Router()


@router.callback_query(MainMenu.main_page, F.data.contains('delete_favourite_product_'))
async def delete_favourite_product(callback: CallbackQuery):
    number_product = int(callback.data[-1])
    favourites_products = get_information('users_favorites', user_id=callback.from_user.id)[
        'favourites_products'].split(';')
    favourites_products.pop(number_product - 1)
    if len(favourites_products) == 0:
        await callback.message.delete()
        favourites_products = None
        update_information('users_info', user_id=callback.from_user.id, number_selected_products=0)
        update_information('users_favorites', user_id=callback.from_user.id,
                           favourites_products=favourites_products)
    else:
        await callback.message.edit_reply_markup(reply_markup=await view_favourite_products(favourites_products))
        update_information('users_favorites', user_id=callback.from_user.id,
                           favourites_products=';'.join(favourites_products))
        update_information('users_info', user_id=callback.from_user.id,
                           number_selected_products=len(favourites_products))


@router.callback_query(MainMenu.main_page, F.data.contains('favourite_product_'))
async def view_fullname_product(callback: CallbackQuery):
    number_product = int(callback.data[-1])
    favourites_products = get_information('users_favorites', user_id=callback.from_user.id)[
        'favourites_products'].split(';')
    await callback.answer(favourites_products[number_product - 1], show_alert=False)
