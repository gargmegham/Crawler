from selenium import webdriver
import json
from bs4 import BeautifulSoup
import time

if __name__ == "__main__":
    links = json.load(open("dev_agency_links.json", 'r'))
    driver = webdriver.Chrome()
    linkedin_links = {}
    total_links = len(links)
    chunk_size = 5
    chunks = [links[i:i + chunk_size] for i in range(0, total_links, chunk_size)]
    for chunk in chunks:
        print(f"Scraping {len(chunk)} links...")
        for link in chunk:
            print(f"Scraping {link}...")
            driver.get(link)
            html_content = driver.page_source
            if link not in linkedin_links:
                linkedin_links[link] = set()
            soup = BeautifulSoup(html_content, "html.parser")
            all_links = soup.find_all("a")
            for a in all_links:
                if a.has_attr("href"):
                    if "linkedin.com" in a["href"]:
                        linkedin_links[link].add(a["href"])
            linkedin_links[link] = list(linkedin_links[link])
        json.dump(linkedin_links, open(f"linkedin_links.json", "w"), indent=4)
    driver.quit()