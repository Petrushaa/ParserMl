import csv
import time
from gets_urls import get_news_urls
from finam_parser import parse_finam_news
from MoscowAPI import get_prices_with_offsets
from pathUrls import extract_news_urls_from_file


def main():
    sitemap_url = "https://www.finam.ru/cache/sitemaps/sitemap_publications_companies.xml"
    output_csv = "finam_news.csv"

    # === 1. Получаем все ссылки из sitemap ===
    # print("📡 Загружаем ссылки из sitemap...")
    # urls = get_news_urls(sitemap_url)
    # print(f"✅ Найдено {len(urls)} ссылок")
    
    urls = extract_news_urls_from_file("finam_companies_sitemap.xml")

    # === 2. Подготовка CSV ===
    with open(output_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # ⚙️ правильные заголовки столбцов
        writer.writerow(["text", "ticker", "price_news", "price_1d", "price_7d"])

        # === 3. Обработка каждой новости ===
        for i, item in enumerate(urls, start=1):
            url = item.url
            print(f"\n[{i}/{len(urls)}] 📰 Парсим новость: {url}")

            try:
                news = parse_finam_news(url)

                # Пропускаем новости без тикеров
                if not news["tickers"]:
                    print("⚠️ Нет тикеров, пропускаем новость.")
                    continue

                # === 4. Для каждого тикера получаем цены 
                for ticker in news["tickers"]:
                    price_news, price_1d, price_7d = get_prices_with_offsets(ticker, news["date"])
                    if price_news == None or price_1d == None or price_7d == None:
                        print("Такого тикера нет скипаю", ticker)
                        continue

                    writer.writerow([
                        news["text"],
                        ticker,
                        price_news,
                        price_1d,
                        price_7d
                    ])

                    print(f"💰 {ticker}: {price_news} → +1д {price_1d} → +7д {price_7d}")

                # 💾 сохраняем прогресс после каждой новости
                f.flush()
                time.sleep(2)  # чтобы не спамить MOEX и Finam

            except Exception as e:
                print(f"❌ Ошибка при обработке {url}: {e}")
                continue

    print("\n✅ Всё готово! Результаты сохранены в:", output_csv)


if __name__ == "__main__":
    main()
