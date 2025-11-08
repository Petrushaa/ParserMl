from dataclasses import dataclass

@dataclass
class NewsUrl:
    url: str
    lastmod: str

@dataclass
class NewsItem:
    url: str
    title: str
    text: str
    ticker: str
