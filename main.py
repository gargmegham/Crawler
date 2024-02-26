from selenium import webdriver
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


def find_linkedin_link(webpage: str):
    driver = webdriver.Chrome()
    driver.get(webpage)
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")
    linkedin_links = set()
    all_links = soup.find_all("a")
    for a in all_links:
        if a.has_attr("href"):
            if "https://www.linkedin.com/company/" in a["href"]:
                clean_link = a["href"].split("?")[0]
                linkedin_links.add(clean_link)
    driver.quit()
    return list(linkedin_links)
