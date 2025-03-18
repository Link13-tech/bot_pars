import os
import datetime
import pandas as pd
from aiogram import Router, F
from aiogram.types import Message, ContentType
from database.db import save_data

router = Router()


@router.message(F.content_type == ContentType.DOCUMENT)
async def handle_document(message: Message):
    if message.document.mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        file_id = message.document.file_id
        file = await message.bot.get_file(file_id)
        file_path = file.file_path

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        download_dir = os.path.join(base_dir, "downloads")
        os.makedirs(download_dir, exist_ok=True)

        file_name = f"items_data_{timestamp}.xlsx"
        download_path = os.path.join(download_dir, file_name)
        await message.bot.download_file(file_path, destination=download_path)

        df = pd.read_excel(download_path)

        required_columns = {"title", "url", "css_selector"}
        if not required_columns.issubset(df.columns):
            await message.answer("Ошибка: В файле должны быть колонки title, url, css_selector.")
            return

        for _, row in df.iterrows():
            await save_data(row["title"], row["url"], row["css_selector"])

        file_content = "\n".join([
            f"Title: {row['title']}\nURL: {row['url']}\nCSS Selector: {row['css_selector']}"
            for _, row in df.iterrows()
        ])

        await message.answer(f"Файл загружен успешно! Данные сохранены в БД. Вот его содержимое:\n{file_content}")
    else:
        await message.answer("Пожалуйста, загрузите файл Excel.")
