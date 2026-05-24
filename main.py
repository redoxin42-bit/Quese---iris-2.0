import asyncio
from aiogram import Bot, Dispatcher
from database import init_db
from handlers import router as main_router

async def main():
    # 1. Запускаем создание таблиц SQLite
    init_db()
    print(" База данных SQLite успешно инициализирована.")

    # 2. Токен бота
    BOT_TOKEN = "8822397260:AAENtI61blt8wHKjo2VsMgIVYVTeUGfqgWY"
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # 3. Подключаем обработчики
    dp.include_router(main_router)

    print("Quese бот наху крутой")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен.")
