import asyncio
import logging
import sys
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram import types, F
from handlers.start import router as start_router
from handlers.upload import router as upload_router
from database.db import init_db

# Загружаем переменные окружения
load_dotenv()

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Токен бота не найден. Убедитесь, что он есть в файле .env")

# Создаем бота и диспетчер
bot = Bot(
    token=BOT_TOKEN,
    session=AiohttpSession(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

# Подключаем роутеры
dp.include_router(start_router)
dp.include_router(upload_router)


@dp.message(F.text.lower() == "/description")
async def description_command(message: types.Message):
    """Описание бота."""
    await message.answer(
        "Этот бот позволяет загружать файлы Excel, которые будут использованы для парсинга сайтов. "
        "Вы можете загрузить данные, и бот будет их обрабатывать для получения информации о товарах."
    )


async def main() -> None:
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
