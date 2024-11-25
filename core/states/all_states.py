from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    write_city = State()


class MainMenu(StatesGroup):
    main_page = State()
    await_page = State()


class SearchProduct(StatesGroup):
    write_name_product = State()
    choose_market = State()
    view_products = State()


class ChangeCity(StatesGroup):
    write_new_city = State()