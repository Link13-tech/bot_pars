import os
import pandas as pd
from aiogram import Router, F
from aiogram.types import Message, ContentType
from database.db import save_data

router = Router()


@router.message(F.content_type == ContentType.DOCUMENT)
async def handle_document(message: Message):
    # Проверяем тип файла (Excel)
    if message.document.mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        file_id = message.document.file_id
        file = await message.bot.get_file(file_id)
        file_path = file.file_path
        file_name = message.document.file_name

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        download_dir = os.path.join(base_dir, "downloads")
        os.makedirs(download_dir, exist_ok=True)

        # Путь для сохранения файла
        download_path = os.path.join(download_dir, file_name)
        await message.bot.download_file(file_path, destination=download_path)

        # Открываем файл с помощью pandas
        df = pd.read_excel(download_path)

        # Проверка на нужные колонки
        required_columns = {"title", "url", "xpath"}
        if not required_columns.issubset(df.columns):
            await message.answer("Ошибка: В файле должны быть колонки title, url, xpath.")
            return

        # Сохраняем данные в БД
        for _, row in df.iterrows():
            await save_data(row["title"], row["url"], row["xpath"])

        file_content = "\n".join([f"Title: {row['title']}, URL: {row['url']}, XPath: {row['xpath']}" for _, row in df.iterrows()])

        await message.answer(f"Файл загружен успешно! Данные сохранены в БД. Вот его содержимое:\n{file_content}")
    else:
        await message.answer("Пожалуйста, загрузите файл Excel.")
