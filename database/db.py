import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_data.sqlite3.1")


async def init_db():
    """Создаёт таблицу в базе данных, если её нет, и саму базу данных, если она не существует."""
    # Проверяем, существует ли папка для базы данных
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Подключаемся к базе данных, создадим её, если она не существует
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(""" 
            CREATE TABLE IF NOT EXISTS parsed_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                xpath TEXT NOT NULL
            )
        """)
        await db.commit()


async def save_data(title: str, url: str, xpath: str):
    """Сохраняет данные из Excel в БД, если такие данные еще не существуют."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Проверяем, существует ли уже товар с таким URL и Xpath
        cursor = await db.execute("SELECT id FROM parsed_data WHERE url = ? AND xpath = ?", (url, xpath))
        existing_data = await cursor.fetchone()

        if existing_data:
            print("Данные с таким URL и Xpath уже существуют.")
            return

        # Если таких данных нет, добавляем их в базу
        await db.execute(
            "INSERT INTO parsed_data (title, url, xpath) VALUES (?, ?, ?)",
            (title, url, xpath),
        )
        await db.commit()
        print("Данные успешно добавлены.")


async def get_all_data():
    """Получает все данные из БД."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT title, url, xpath FROM parsed_data")
        rows = await cursor.fetchall()
        return rows
