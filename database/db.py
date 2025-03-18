import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_data.sqlite3.1")


async def init_db():
    """Создаёт таблицы в базе данных, если их нет."""
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

        await db.execute("""
            CREATE TABLE IF NOT EXISTS last_uploaded (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                css_selector TEXT NOT NULL
            )
        """)

        await db.commit()


async def save_data(title: str, url: str, css_selector: str):
    """Сохраняет данные в БД, если их ещё нет в основной таблице, и всегда добавляет в `last_uploaded`."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id FROM parsed_data WHERE title = ? AND url LIKE ?", (title, f"%{url}%"))
        existing_data = await cursor.fetchone()

        if existing_data:
            print(f"Данные '{title}' уже есть в базе (в таблице parsed_data).")
        else:
            await db.execute("INSERT INTO parsed_data (title, url, css_selector) VALUES (?, ?, ?)", (title, url, css_selector))
            await db.commit()
            print(f"Данные '{title}' добавлены в parsed_data.")

        await db.execute("INSERT INTO last_uploaded (title, url, css_selector) VALUES (?, ?, ?)", (title, url, css_selector))
        await db.commit()
        print(f"Данные '{title}' добавлены в last_uploaded.")


async def get_last_uploaded_data():
    """Возвращает последние загруженные данные."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT title, url, css_selector FROM last_uploaded")
        rows = await cursor.fetchall()
        return rows


async def clear_last_uploaded():
    """Очищает таблицу `last_uploaded` после парсинга."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM last_uploaded")
        await db.commit()
