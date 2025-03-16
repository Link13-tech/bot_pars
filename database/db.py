import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_data.sqlite3.1")


async def init_db():
    """Создаёт таблицу в базе данных, если её нет."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(""" 
            CREATE TABLE IF NOT EXISTS parsed_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                css_selector TEXT NOT NULL
            )
        """)
        await db.commit()


async def save_data(title: str, url: str, css_selector: str):
    """Сохраняет данные в БД, если их ещё нет."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id FROM parsed_data WHERE title = ? AND url LIKE ?", (title, f"%{url}%"))
        existing_data = await cursor.fetchone()

        if existing_data:
            print("Данные с таким title уже существуют.")
            return

        await db.execute(
            "INSERT INTO parsed_data (title, url, css_selector) VALUES (?, ?, ?)",
            (title, url, css_selector),
        )
        await db.commit()
        print("Данные успешно добавлены.")


async def get_all_data():
    """Получает все данные из БД."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT title, url, css_selector FROM parsed_data")
        rows = await cursor.fetchall()
        return rows
