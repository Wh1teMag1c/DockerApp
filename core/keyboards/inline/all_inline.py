from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder

settings_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⚙Изменить город', callback_data='edit_city')]
])


async def view_favourite_products(products):
    favourite_products_menu = InlineKeyboardBuilder()
    for _ in range(len(products)):
        favourite_products_menu.add(InlineKeyboardButton(text=products[_], callback_data=f'favourite_product_{_ + 1}'))
        favourite_products_menu.add(
            InlineKeyboardButton(text='❌Удалить', callback_data=f'delete_favourite_product_{_ + 1}'))
    return favourite_products_menu.adjust(2).as_markup()


async def view_products_menu(current_page, all_pages):
    products_menu = InlineKeyboardBuilder()
    products_menu.add(InlineKeyboardButton(text='◀Назад', callback_data='back_page'))
    products_menu.add(InlineKeyboardButton(text=f'{current_page}/{all_pages}', callback_data='count_pages'))
    products_menu.add(InlineKeyboardButton(text=f'Вперёд▶', callback_data='next_page'))
    products_menu.row(InlineKeyboardButton(text=f'❌Закрыть', callback_data='close_menu_products'))
    return products_menu.as_markup()


async def adding_to_favourites(flag):
    adding_to_favorites_menu = InlineKeyboardBuilder()
    if flag:
        adding_to_favorites_menu.add(InlineKeyboardButton(text='Добавить в ⭐', callback_data='add_favorite'))
    adding_to_favorites_menu.add(InlineKeyboardButton(text='❌Закрыть', callback_data='close_menu_products'))
    return adding_to_favorites_menu.as_markup()
