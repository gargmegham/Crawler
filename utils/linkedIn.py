import time
from random import randint

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from utils import extract_soup_text


def linkedin_login(driver: webdriver.Chrome, secrets: dict):
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


def linkedin_scroll(driver: webdriver.Chrome):
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            driver.find_element(by=By.CLASS_NAME, value="artdeco-loader__bars")
        except NoSuchElementException:
            break


def linkedin_get_company_logo(driver: webdriver.Chrome):
    try:
        company_logo_image = driver.find_element(
            by=By.CSS_SELECTOR, value="img.org-top-card-primary-content__logo"
        )
        company_logo = company_logo_image.get_attribute("src")
        if company_logo.startswith("data:image"):
            return None
        return company_logo
    except NoSuchElementException:
        return None


def linkedin_wait(driver: webdriver.Chrome):
    """
    while element with class artdeco-loader is present in the page
    """
    while True:
        try:
            driver.find_element(by=By.CLASS_NAME, value="artdeco-loader")
        except NoSuchElementException:
            break


def linkedin_get_company_executives(driver: webdriver.Chrome):
    try:
        company_people = driver.find_elements(
            by=By.CSS_SELECTOR, value="div.org-people-profile-card__profile-info"
        )
        people_info = list()
        for person in company_people:
            try:
                person_name = extract_soup_text(
                    person.find_element(
                        by=By.CSS_SELECTOR,
                        value="div.org-people-profile-card__profile-title",
                    )
                )
                if person_name.startswith("LinkedIn"):
                    continue
                person_position = extract_soup_text(
                    person.find_element(
                        by=By.XPATH,
                        value="//div[contains(@class, 'artdeco-entity-lockup__subtitle')]",
                    )
                )
                person_linkedin = person.find_element(
                    by=By.XPATH,
                    value="//div[contains(@class, 'artdeco-entity-lockup__content')]//div/a",
                ).get_attribute("href")
                person_image = person.find_element(
                    by=By.CSS_SELECTOR, value="img.evi-image"
                ).get_attribute("src")
                if person_image.startswith("data:image"):
                    person_image = None
                people_info.append(
                    {
                        "name": person_name,
                        "position": person_position,
                        "linkedin": person_linkedin,
                        "image": person_image,
                    }
                )
            except NoSuchElementException:
                continue
        return people_info
    except NoSuchElementException:
        return []
