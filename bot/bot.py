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
from parser.parser import get_data_from_db

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Токен бота не найден. Убедитесь, что он есть в файле .env")

bot = Bot(
    token=BOT_TOKEN,
    session=AiohttpSession(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(start_router)
dp.include_router(upload_router)


@dp.message(F.text.lower() == "/description")
async def description_command(message: types.Message):
    """Описание бота."""
    await message.answer(
        "Этот бот позволяет загружать файлы Excel, которые будут использованы для парсинга сайтов. "
        "Вы можете загрузить данные, и бот будет их обрабатывать для получения информации о товарах."
    )


@dp.message(F.text.lower() == "/items")
async def show_items(message: types.Message):
    """Выводит все товары из базы данных и их цены."""
    # Получаем товары из базы данных
    items = get_data_from_db()
    if items:
        response = "Список товаров:\n"
        for title, url, price in items:
            response += f"{title} - {price} руб.\n\n" if price else f"{title} - Цена не найдена.\n\n"
        await message.answer(response)
    else:
        await message.answer("Товары не найдены в базе данных.")


async def main() -> None:
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
