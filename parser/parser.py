import sqlite3
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import re
import time
import logging
from selenium.webdriver.common.keys import Keys
from database.db import DB_PATH

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def clean_price(price_str):
    """Очищает строку цены от лишних символов (например, пробелов или валютных символов)."""
    logger.debug(f"Исходная строка цены: {price_str}")
    cleaned_price = re.sub(r'[^\d,.]', '', price_str)
    logger.debug(f"Очищенная строка цены: {cleaned_price}")
    return cleaned_price


def initialize_driver():
    """Инициализирует драйвер для парсинга с использованием chromedriver-autoinstaller."""
    try:
        chromedriver_autoinstaller.install()

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=options)
        return driver

    except Exception as e:
        logger.error(f"Ошибка при инициализации драйвера: {e}")
        return None


def get_prices_from_search_page(url, item_name, css_selector, search_input_selector):
    """Получает цены со страницы поиска, используя указанный CSS-селектор."""
    driver = initialize_driver()
    if not driver:
        return []

    driver.implicitly_wait(5)
    driver.get(url)
    time.sleep(2)

    try:
        find_input = WebDriverWait(driver, 2).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, search_input_selector))
        )
        find_input.clear()
        find_input.send_keys(item_name)
        time.sleep(2)

        find_input.send_keys(Keys.ENTER)
        time.sleep(2)

        price_elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
        prices = [clean_price(element.text) for element in price_elements]
        logger.debug(f"Цены с страницы: {prices}")

    except Exception as e:
        logger.error(f"Ошибка при сборе цен с страницы поиска: {e}")
        prices = []

    driver.quit()
    return prices


def parse_and_get_average_price(url, title, css_selector, search_input_selector):
    """Парсит цены на странице поиска и вычисляет среднюю цену."""
    prices = get_prices_from_search_page(url, title, css_selector, search_input_selector)

    if prices:
        prices = [float(price.replace(',', '.')) for price in prices if price]
        if prices:
            average_price = sum(prices) / len(prices)
            logger.debug(f"Средняя цена для {title}: {average_price}")
            return round(average_price, 2)

    logger.debug(f"Цены не найдены для {title}")
    return None


def get_data_from_db():
    """Забирает данные из базы, парсит цены с поиска и возвращает результат."""
    try:
        logger.debug("Подключаемся к базе данных")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT title, url, css_selector FROM parsed_data")
        rows = cursor.fetchall()
        conn.close()
        logger.debug(f"Найдено {len(rows)} записей в базе")

        results = []
        for title, url, css_selector in rows:
            logger.debug(f"Обрабатываем товар: {title}, URL: {url}, CSS Selector: {css_selector}")
            if "wildberries" in url.lower():
                search_input_selector = "#searchInput"
            else:
                search_input_selector = "[name='text']"

            average_price = parse_and_get_average_price(url, title, css_selector, search_input_selector)
            if average_price is not None:
                logger.debug(f"Средняя цена для {title}: {average_price}")
            results.append((title, url, average_price))

        logger.debug("Все цены обработаны")
        return results
    except sqlite3.Error as e:
        logger.error(f"Ошибка при подключении к базе данных: {e}")
        return []
    except Exception as e:
        logger.error(f"Неизвестная ошибка при получении данных из базы: {e}")
        return []
