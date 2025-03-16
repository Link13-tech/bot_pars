from aiogram import Router, types, F
from parser.parser import get_data_from_db

router = Router()


@router.message(F.text.lower() == "/items")
async def show_items(message: types.Message):
    """Выводит все товары из базы данных и их цены."""
    items = get_data_from_db()
    if items:
        response = "Список товаров:\n"
        for title, url, price in items:
            response += f"<b>{title}</b> - {url} - <b>Средняя цена:</b> {price} руб.\n\n" if price else f"{title} - Цена не найдена.\n\n"
        await message.answer(response)
    else:
        await message.answer("Товары не найдены в базе данных.")