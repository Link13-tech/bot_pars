from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from parser.parser import parse_all_items, parse_last_uploaded_items
from database.db import clear_last_uploaded
import asyncio
from aiogram.utils.chat_action import ChatActionSender

router = Router()


@router.message(F.text.lower() == "/items")
async def ask_parsing_mode(message: types.Message):
    """Выводит кнопки выбора режима парсинга."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Парсить всю базу", callback_data="parse_all")],
        [InlineKeyboardButton(text="🆕 Парсить только загруженные", callback_data="parse_uploaded")]
    ])
    await message.answer("Выберите режим парсинга:", reply_markup=keyboard)


@router.callback_query(lambda c: c.data in ["parse_all", "parse_uploaded"])
async def start_parsing(callback: CallbackQuery):
    """Обрабатывает выбор режима парсинга."""
    bot = callback.bot
    await callback.answer()
    await callback.message.delete()

    loading_message = await callback.message.answer("⏳ Ожидайте, идет обработка данных...")
    # sticker = await callback.message.answer_sticker("CAACAgIAAxkBAAEFgFZlKThlZx3nVjX1E8eBQnG3YxRPWAACAwADr8ZRGk_tuAABU6NvNAQ")

    async with ChatActionSender.typing(bot=bot, chat_id=callback.message.chat.id):
        await asyncio.sleep(3)

        if callback.data == "parse_all":
            items = parse_all_items()
        else:
            items = parse_last_uploaded_items()
            await clear_last_uploaded()

    await loading_message.delete()
    # await sticker.delete()

    if items:
        response = "📦 Список товаров:\n"
        for title, url, price in items:
            response += f"<b>{title}</b> - {url} - <b>Средняя цена:</b> {price} руб.\n\n" if price else f"{title} - Цена не найдена.\n\n"
        await callback.message.answer(response)
    else:
        await callback.message.answer("⚠️ Товары не найдены в базе данных.")
