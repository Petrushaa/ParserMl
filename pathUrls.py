from typing import List
import xml.etree.ElementTree as ET
from schemas import NewsUrl




def extract_news_urls_from_file(xml_filename: str) -> List[NewsUrl]:
    tree = ET.parse(xml_filename)           # читаем XML-файл
    root = tree.getroot()                   # получаем корневой элемент
    news_urls = []
    ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}  # namespace
    for url_elem in root.findall('ns:url', ns):
        loc = url_elem.find('ns:loc', ns).text if url_elem.find('ns:loc', ns) is not None else ''
        lastmod = url_elem.find('ns:lastmod', ns).text if url_elem.find('ns:lastmod', ns) is not None else ''
        news_urls.append(NewsUrl(url=loc, lastmod=lastmod))
    return news_urls[3000:]


if __name__ == "__main__":
    news = extract_news_urls_from_file("finam_companies_sitemap.xml")
    for new in news[5000::]:
        print(f"URL: {new.url}, Last Modified: {new.lastmod}")