from aiogram import Router
from aiogram.types import Message
from aiogram import F

router = Router()


@router.message(F.text.lower() == "/start")
async def start(message: Message):
    await message.answer("Привет! Загрузите файл Excel, чтобы я начал работу с ним.")
