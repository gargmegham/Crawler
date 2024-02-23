from selenium import webdriver
import json
from bs4 import BeautifulSoup
import time

def find_links(base_url: str, total_pages: int):
    links = []
    for page in range(0, total_pages):
        driver = webdriver.Chrome()
        driver.get(f"{base_url}?page={page}&sort_by=ClutchRank")
        time.sleep(10)
        html_content = driver.page_source
        driver.quit()
        soup = BeautifulSoup(html_content, "html.parser")
        dirty_links = soup.find_all("li", class_="website-link")
        for link in dirty_links:
            link = link.find("a", class_="website-link__item")
            if link and link.has_attr("href"):
                link = link["href"]
                if "ppc.clutch.co" not in link:
                    links.append(link)
    return links


def clean_links(links: list):
    unique_links = set()
    for link in links:
        clean_link = link.split('?')[0]
        if clean_link.endswith('/'):
            clean_link = clean_link[:-1]
        unique_links.add(clean_link)
    unique_links = list(unique_links)
    return unique_links


if __name__ == "__main__":
    start_time = time.time()
    links = find_links("https://clutch.co/us/web-developers", 270)
    unique_links = clean_links(links)
    json.dump(unique_links, open(f"USA.json", "w"), indent=4)
