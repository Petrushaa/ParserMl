from playwright.sync_api import sync_playwright
import time
from datetime import datetime
import re


def parse_finam_news(url: str) -> dict:
    """
    Парсит новость с Finam:
    - Заголовок
    - Текст
    - Дата публикации
    - Только тикеры акций из блока quote-info
    """

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False — для отладки
        
        page = browser.new_page()
        page.goto(url)
        with open("some.html", "w", encoding="utf-8") as f:
            f.write(page.content())

        # === Раскрыть скрытые акции, если есть кнопка ===
        try:
            page.locator("span[data-name='toggle']").click(timeout=1000)
        except:
            pass

        # === Заголовок и текст ===
        title = page.locator("h1").inner_text()
        text = page.locator("div[data-id='text']").inner_text()

        # === Дата и время из URL ===
        match = re.search(r"(\d{8})-(\d{4})", url)
        if match:
            date_str, time_str = match.groups()
            dt_news = datetime.strptime(date_str + time_str, "%Y%m%d%H%M")
        else:
            dt_news = None

        # === Только нужные тикеры из блока quote-info ===
        tickers = set()
        quote_blocks = page.locator("div[data-id='quote-info']")

        for i in range(quote_blocks.count()):
            block = quote_blocks.nth(i)
            links = block.locator("a[href*='/quote/moex/']").all()
            for link in links:
                href = link.get_attribute("href")
                match = re.search(r"/quote/moex/([a-z0-9]+)/", href)
                if match:
                    ticker = match.group(1).upper()
                    tickers.add(ticker)

        browser.close()

    return {
        "url": url,
        "text": title + "\n" + text,
        "date": dt_news,
        "tickers": list(tickers),
    }


if __name__ == "__main__":
    test_url = "https://www.finam.ru/publications/item/rynok-ispolzuet-dlya-podema-lyubye-vozmozhnosti-20251030-1436/"
    data = parse_finam_news(test_url)

    print(f"📅 Дата: {data['date']}")
    print(f"📊 Тикеры: {data['tickers']}")
    print("\n📄 Текст:\n", data['text'])
