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
from bot.handlers.start import router as start_router
from bot.handlers.upload import router as upload_router
from bot.handlers.items import router as items_router
from database.db import init_db

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
dp.include_router(items_router)


# Обработчик команды /description
@dp.message(F.text.lower() == "/description")
async def description_command(message: types.Message):
    """Описание бота."""
    await message.answer(
        "Этот бот позволяет загружать файлы Excel, которые будут использованы для парсинга сайтов. "
        "Вы можете загрузить данные, и бот будет их обрабатывать для получения информации о товарах.\n\n"
        "Файл Excel должен содержать три обязательных столбца:\n"
        "<b>title</b>: название товара\n"
        "<b>url</b>: ссылка маркетплейса (OZON, WB)\n"
        "<b>css_selector</b>: CSS-селектор для парсинга данных\n\n"
        "После загрузки файла, нажмите команду /items для начала парсинга."
    )


# Обработчик для неизвестных сообщений
@dp.message(lambda message: message.text and not message.text.startswith('/') and not message.document)
async def handle_unknown_message(message: types.Message):
    """Обрабатывает любые сообщения, не являющиеся командами, и информирует пользователя о командах."""
    await message.answer(
        "Пожалуйста, используйте одну из команд:\n"
        "/start - для начала работы\n"
        "/description - для получения информации о боте\n"
        "/items - для отображения товаров из базы данных"
    )


async def main() -> None:
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
