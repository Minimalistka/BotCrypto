import asyncio
from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
import sqlite3
import os
from handlers import handlers


# Главная асинхронная функция для запуска бота
async def main():
    config: Config = load_config()
    # Создание объекта бота
    bot = Bot(token=config.tg_bot.token)
    # Создание диспетчера для обработки сообщений и команд
    dp = Dispatcher()
    dp.include_router(handlers.router)


    # Запускаем long polling для получения обновлений
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


    # Настройка базы данных SQLite для хранения пользователей
    if not os.path.exists("currency.db"):
        conn = sqlite3.connect("currency.db")
        cursor = conn.cursor()
        # Создаём таблицу, если её ещё нет
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)")
        conn.commit()
        conn.close()

# Точка входа в программу
if __name__ == "__main__":
    import sys
    # Устанавливаем политику для событийного цикла на Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
