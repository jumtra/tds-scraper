import requests  # noqa: INP001
from bs4 import BeautifulSoup


def get_text_from_url(url: str) -> BeautifulSoup:
    """Simple scraper."""  # noqa: D401
    # Responseオブジェクト生成
    response = requests.get(url=url, timeout=60)
    # 文字化け防止
    response.encoding = response.apparent_encoding
    # BeautifulSoupオブジェクト生成
    return BeautifulSoup(response.text, "html.parser")
