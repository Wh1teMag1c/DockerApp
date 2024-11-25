from core.handlers.users import main_menu, main_start, profile_menu, search_product, favourite_products_menu
from core.utils.commands import set_commands
from core.utils.db_api.api_sqlite import create_bdx
from core.utils.parser_edadeal.parser_favourites_products import create_tasks
from loader import dp, bot, scheduler
import asyncio
import logging


async def scheduler_start():
    scheduler.add_job(create_tasks, "cron", hour='7', timezone='Europe/Moscow')


async def start():
    dp.include_routers(main_menu.router, main_start.router, profile_menu.router, search_product.router,
                       favourite_products_menu.router)
    await set_commands(bot)
    await scheduler_start()
    scheduler.start()
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO)
    create_bdx()
    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        print('Бот остановлен!')
