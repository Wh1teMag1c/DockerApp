from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton)

main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🔍 Поиск')],
    [KeyboardButton(text='👤 Профиль'), KeyboardButton(text='⭐ Избранное')]
],
    resize_keyboard=True)

back_button = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='◀ Назад')]
],
    resize_keyboard=True)

