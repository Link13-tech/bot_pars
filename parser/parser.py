import sqlite3
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import re
import time
import logging

from database.db import DB_PATH

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def clean_price(price_str):
    """Очистка строки от ненужных символов, но без преобразования в число."""
    logger.debug(f"Исходная строка цены: {price_str}")

    # Убираем все символы, кроме цифр и возможного разделителя (запятой/точки)
    cleaned_price = re.sub(r'[^\d,.]', '', price_str)

    logger.debug(f"Очищенная строка цены: {cleaned_price}")

    return cleaned_price


def initialize_driver():
    """Инициализация undetected_chromedriver с дополнительными проверками."""
    options = uc.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    try:
        driver = uc.Chrome(options=options)
        return driver
    except Exception as e:
        logger.error(f"Ошибка при инициализации драйвера: {e}")
        return None


def parse_price(url, xpath):
    """Парсит цену с указанного URL, используя переданный XPath."""
    if not xpath:  # Проверка на None или пустую строку
        print(f"Ошибка: XPath для {url} не указан или пуст.")
        return None

    driver = uc.Chrome()
    driver.get(url)

    # Добавляем задержку, чтобы дать странице время для полной загрузки
    time.sleep(3)

    try:
        # Явное ожидание появления элемента
        element = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, xpath))
        )
        logger.debug(f"Найден элемент для URL: {url}, текст элемента: {element.text}")

        price_str = clean_price(element.text)
        logger.debug(f"Строка цены после очистки: {price_str}")

    except Exception as e:
        price_str = None
        logger.error(f"Ошибка при парсинге {url}: {e}")

    driver.quit()
    return price_str


def get_prices_from_db():
    """Забирает данные из SQLite, парсит цены и возвращает результат без сохранения в БД."""
    try:
        logger.debug("Подключаемся к базе данных")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT title, url, xpath FROM parsed_data")
        rows = cursor.fetchall()
        conn.close()
        logger.debug(f"Найдено {len(rows)} записей в базе")

        results = []
        for title, url, xpath in rows:
            logger.debug(f"Обрабатываем товар: {title}, URL: {url}, XPath: {xpath}")
            price = parse_price(url, xpath)
            logger.debug(f"Цена получена: {price}")
            results.append((title, url, price))

        logger.debug("Все цены обработаны")
        return results
    except sqlite3.Error as e:
        logger.error(f"Ошибка при подключении к базе данных: {e}")
        return []
    except Exception as e:
        logger.error(f"Неизвестная ошибка при получении данных из базы: {e}")
        return []
