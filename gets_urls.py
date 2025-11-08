import requests
import xmltodict
from datetime import datetime, timedelta
from schemas import NewsUrl
from pathlib import Path


def get_news_urls(map_url: str) -> list[NewsUrl]:
    """
    Загружает sitemap Finam и возвращает только те новости,
    которые старше 7 дней (по тегу <lastmod>).
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        )
    }

    response = requests.get(map_url, headers=headers, timeout=15)
    response.raise_for_status()

    xml_bytes = response.content.lstrip(b'\xef\xbb\xbf')
    xml_text = xml_bytes.decode("utf-8")

    data_dict = xmltodict.parse(xml_text)
    urls_list = data_dict.get("urlset", {}).get("url", [])

    cutoff_date = datetime.now() - timedelta(days=9)
    res: list[NewsUrl] = []

    for item in urls_list:
        url = item.get("loc")
        lastmod = item.get("lastmod")
        if not url or not lastmod:
            continue

        try:
            news_date = datetime.strptime(lastmod, "%Y-%m-%d")
            # print(f"Проверка: {url} -> {news_date}")

            if news_date < cutoff_date:
                # print(url, news_date)
                res.append(NewsUrl(url=url, lastmod=lastmod))
        except Exception as e:
            print(f"⚠️ Ошибка даты у {url}: {e}")
            continue

    return res


def save_urls_to_file(urls: list[NewsUrl], filename: str = "data/urls.txt"):
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        for url in urls:
            f.write(url.url + "\n")

    print(f"✅ Ссылки сохранены в {path}")


if __name__ == "__main__":
    urls = get_news_urls("https://www.finam.ru/cache/sitemaps/sitemap_publications_companies.xml")
    print(f"✅ Получено ссылок старше недели: {len(urls)}")
    #save_urls_to_file(urls)
