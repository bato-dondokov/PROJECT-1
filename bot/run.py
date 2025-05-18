import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import auth_router, expert_router, admin_router
from database.models import async_main


async def main():
    await async_main()
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(auth_router)
    dp.include_router(expert_router)
    dp.include_router(admin_router)
    await dp.start_polling(bot)


if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit') 