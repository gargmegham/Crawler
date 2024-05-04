from bs4 import BeautifulSoup


def extract_soup_text(soup: BeautifulSoup) -> str:
    return soup.text.strip() if soup else ""
