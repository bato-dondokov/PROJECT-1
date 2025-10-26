import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import TOKEN
from handlers import auth_router, expert_router, admin_router
from database.models import async_main
from queue_manager import model_worker


"""Скрипт для запуска бота"""


def create_data_dir():
    """Создает директорию для хранения данных, если она не существует"""
    xrays_dir = 'bot/xrays'
    teeth_dir = 'bot/teeth'
    os.makedirs(xrays_dir, exist_ok=True)
    os.makedirs(teeth_dir, exist_ok=True)


async def set_default_commands(bot: Bot):
    """Определяет команды по умолчанию"""
    commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/help", description="Помощь"),
    ]
    await bot.set_my_commands(commands)


async def main():
    """Запускает бота и БД"""
    await async_main()
    create_data_dir()
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(auth_router)
    dp.include_router(expert_router)
    dp.include_router(admin_router)
    await set_default_commands(bot)
    asyncio.create_task(model_worker(bot))
    await dp.start_polling(bot)


if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit') 