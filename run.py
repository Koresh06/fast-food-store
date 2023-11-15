import asyncio
import os

from dotenv import load_dotenv, find_dotenv
from aiogram import Bot, Dispatcher
from app.handlers.user_handler import router
from app.handlers.admin_handler import admin
from app.database.models import async_main

from app.middlewares.middlewares import Is_Admin

load_dotenv(find_dotenv())

async def main():
    await async_main() #Запуск БД
    bot: Bot = Bot(token=os.getenv('TOKEN'), parse_mode='HTML')
    dp: Dispatcher = Dispatcher()
    
    dp.message.middleware(Is_Admin())
    dp.include_routers(admin, router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
    
if __name__ == '__main__':
    try:
        print('Бот запущен!')
        asyncio.run(main())
    except KeyboardInterrupt as exx:
        print(exit())