import json
import time
from random import randint

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


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


def find_linkedin_company_people(company_links: list, secrets):
    driver = webdriver.Chrome()
    # login
    driver.get("https://www.linkedin.com/login")
    time.sleep(randint(1, 5))
    username = driver.find_element(value="username")
    username.send_keys(secrets["username"])
    password = driver.find_element(value="password")
    password.send_keys(secrets["password"])
    login_button = driver.find_element(
        by=By.XPATH, value='//*[@id="organic-div"]/form/div[3]/button'
    )
    login_button.click()
    time.sleep(randint(1, 5))
    # go to company page, and click on people
    for company_link in company_links:
        try:
            driver.get(f"{company_link}/people/")
            time.sleep(randint(1, 5))
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(randint(1, 5))
                try:
                    driver.find_element(by=By.CLASS_NAME, value="artdeco-loader__bars")
                except NoSuchElementException:
                    break
            time.sleep(randint(1, 5))
            html_content = driver.page_source
            with open(f"htmls/{company_link.split('/')[-1]}.html", "w") as file:
                file.write(html_content)
        except NoSuchElementException:
            time.sleep(randint(1, 5))
        except:
            pass
    driver.quit()


def process_linkedin_htmls(file_name: str):
    linkedin_links = json.load(open(f"jsons/{file_name}", "r"))
    company_data = {}
    for website in linkedin_links:
        print("Processing: ", website)
        linkedin_link = linkedin_links[website][0]
        html_file = f"htmls/{linkedin_link.split('/')[-1]}.html"
        try:
            with open(html_file, "r") as file:
                html_content = file.read()
        except FileNotFoundError:
            print(f"File not found: {html_file}")
            continue
        soup = BeautifulSoup(html_content, "html.parser")
        company_name = (
            str(soup.find("title").text.split(": People")[0]).replace("\n", "").strip()
        )
        try:
            company_logo = soup.find(
                "img", class_="org-top-card-primary-content__logo"
            ).get("src")
        except AttributeError:
            company_logo = None
        try:
            company_description = (
                str(soup.find("p", class_="org-top-card-summary__tagline").text)
                .replace("\n", "")
                .strip()
            )
        except AttributeError:
            company_description = None
        try:
            company_info = soup.find_all(
                "div", class_="org-top-card-summary-info-list__info-item"
            )
        except AttributeError:
            company_info = None
        company_info_items = [
            str(item.text).replace("\n", "").strip() for item in company_info
        ]
        company_people = soup.find_all(
            "div", class_="org-people-profile-card__profile-info"
        )
        company_people_info = []
        for person in company_people:
            person_name = (
                str(
                    person.find(
                        "div", class_="org-people-profile-card__profile-title"
                    ).text
                )
                .replace("\n", "")
                .strip()
            )
            try:
                person_position = (
                    str(
                        person.find(
                            "div", class_="artdeco-entity-lockup__subtitle"
                        ).div.div.text
                    )
                    .replace("\n", "")
                    .strip()
                )
            except AttributeError:
                continue
            company_people_info.append((person_name, person_position))
        company_data[website] = {
            "linkedin_link": linkedin_link,
            "company_name": company_name,
            "company_logo": company_logo,
            "company_description": company_description,
            "company_info": company_info_items,
            "company_people": company_people_info,
        }
    json.dump(company_data, open("jsons/company_data.json", "w"))


def guess_emails(company_data: dict):
    emails = {}
    for company_website in company_data:
        suffix = company_website.replace("https://", "").replace("http://", "")
        suffix = suffix.split("/")[0]
        company_people = company_data[company_website]["company_people"]
        company_name = company_data[company_website]["company_name"]
        if suffix.startswith("www."):
            suffix = suffix[4:]
        for person in company_people:
            prefix = None
            person_name = str(person[0]).strip().lower()
            person_position = str(person[1]).strip().lower()
            for word in person_name.split(" "):
                if word.endswith("."):
                    continue
                if word == "linkedin":
                    break
                prefix = word
                break
            if prefix:
                email = f"{prefix}@{suffix}"
                emails[email] = [person_name, person_position, company_name]
    return emails
