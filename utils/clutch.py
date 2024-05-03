import logging
import time
from random import randint

from bs4 import BeautifulSoup
from pymongo.collection import Collection
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s",
    filemode="a",
    filename="logs/clutch.log",
)


def apply_filters(
    base_url: str, page: int, min_reviews: int, verified: bool, team_size: int = None
):
    if page > 0:
        base_url += f"&page={page}"
    if verified:
        base_url += "&verification=true"
    if min_reviews in [1, 3, 5, 10, 15, 20]:
        base_url += f"&reviews={min_reviews}"
    if team_size is not None:
        if team_size == 10:
            base_url += "&agency_size=10+-+49"
        elif team_size == 50:
            base_url += "&agency_size=50+-+249"
        elif team_size == 250:
            base_url += "&agency_size=250+-+999"
        elif team_size == 1000:
            base_url += "&agency_size=1%2C000+-+9%2C999"
        elif team_size == 10000:
            base_url += "&agency_size=10%2C000%2B"
    return base_url


def find_directory_links() -> list:
    driver = webdriver.Chrome()
    driver.get("https://clutch.co/sitemap")
    links = driver.find_elements(By.TAG_NAME, "a")
    urls = []
    for link in links:
        if "sitemap-data__wrap-link" in link.get_attribute("class"):
            urls.append(link.get_attribute("href"))
    driver.quit()
    return urls


def find_actual_link_after_redirecting(link: str) -> str:
    driver = webdriver.Chrome()
    driver.get(link)
    time.sleep(randint(1, 5))
    actual_link = driver.current_url
    driver.quit()
    return actual_link


def extract_soup_text(soup: BeautifulSoup) -> str:
    return soup.text.strip() if soup else ""


def find_company_info(company: BeautifulSoup) -> dict:
    name = extract_soup_text(
        company.find("a", class_="company_title")
    ) or company.get("data-title")
    website = company.find("a", class_="website-link__item")
    if not website:
        return {}
    website = website["href"]
    if "/profile/" in website:
        return {}
    tagline = extract_soup_text(company.find("p", class_="company_info__wrap"))
    rating = extract_soup_text(company.find("span", class_="sg-rating__number"))
    reviews_count = extract_soup_text(
        company.find("a", class_="sg-rating__reviews")
    ).replace(" reviews", "")
    min_project_size = company.find("div", class_="list-item block_tag custom_popover")
    if min_project_size:
        min_project_size = extract_soup_text(min_project_size.find("span"))
    else:
        min_project_size = ""
    extra_info = []
    if company.find_all("div", class_="list-item custom_popover"):
        for info in company.find_all("div", class_="list-item custom_popover"):
            extra_info.append(extract_soup_text(info.find("span")))
    if "ppc.clutch.co" in website:
        website = find_actual_link_after_redirecting(website)
    if "?" in website:
        website = website.split("?")[0]
    return {
        "name": name,
        "tagline": tagline,
        "rating": rating,
        "reviews_count": reviews_count,
        "min_project_size": min_project_size,
        "extra_info": extra_info,
        "website": website,
    }


def check_for_error(soup: BeautifulSoup) -> bool:
    try:
        check_error = soup.find("h3", class_="error-type")
        if check_error:
            return True
        return False
    except NoSuchElementException:
        return False


def crawl_company(url: str, driver: webdriver.Chrome) -> tuple:
    print("Crawling: ", url)
    driver.get(url)
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")
    linkedin_links = set()
    emails = set()
    phone_numbers = set()
    for link in soup.find_all("a"):
        href = link.get("href")
        if href:
            if "linkedin.com" in href:
                linkedin_links.add(href)
            if "mailto:" in href:
                emails.add(href.replace("mailto:", ""))
            if "tel:" in href:
                phone_numbers.add(href.replace("tel:", ""))
    print("Linkedin Links: ", linkedin_links)
    print("Emails: ", emails)
    print("Phone Numbers: ", phone_numbers)
    print("*" * 50)
    return list(linkedin_links), list(emails), list(phone_numbers)


def crawl_companies(base_url: str, companies: Collection) -> list:
    page_has_error = False
    current_page = 0
    while not page_has_error:
        print(f"Processing page: {current_page} for {base_url}")
        driver = webdriver.Chrome()
        driver.get(
            apply_filters(
                f"{base_url}?sort_by=ClutchRank",
                current_page,
                verified=True,
                min_reviews=None,
            )
        )
        html_content = driver.page_source
        driver.quit()
        soup = BeautifulSoup(html_content, "html.parser")
        companies_found = soup.find_all("li", class_="provider-row")
        if check_for_error(soup) or not companies_found:
            print(f"Error on page {current_page} for {base_url}")
            break
        for company in companies_found:
            name = extract_soup_text(
                company.find("a", class_="company_title")
            ) or company.get("data-title")
            if companies.find_one({"name": name}):
                print(f"Company already exists: {name}")
                continue
            company_info = find_company_info(company)
            if not company_info.get("website"):
                print(f"Website link not found for {company_info.get('name')}")
                continue
            companies.insert_one(company_info)
            print(f"Company: {company_info.get('name')}")
        else:
            print(f"Page {current_page} processed successfully")
        time.sleep(randint(1, 5))
        current_page += 1
