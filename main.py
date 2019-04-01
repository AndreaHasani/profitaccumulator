from selenium import webdriver
import time
import sys
import itertools
from twilio.rest import Client

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# from multiprocessing import Pool, cpu_count, Lock, Process


# Variables, Can change
delay = 60  # seconds to wait for table to show then exit if not showing
update_delay = 60  # seconds to wait for new values, ex: every 60s

username = "xxxx"
password = "xxxx"
headless = False
rating_limit = 100
backodds_limit = 10
odds_found = []

def sendsms(message):
    ACCOUNT_SID = "xxx"
    AUTH_TOKEN = "xxx"

    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    m = list(itertools.islice(message, 5))

    message = ", ".join(m)
    from_ = "+xxxxxxxxx",

    client.messages.create(
        to="+xxxxxxxx",
        from_=from_,
        body=message,
    )

def main(username, password):
    global odds_found
    chrome_options = webdriver.ChromeOptions()
    if headless:
        chrome_options.add_argument('headless')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.profitaccumulator.co.uk/wp-login.php")

    username_field = driver.find_element_by_id("user_login")
    password_field = driver.find_element_by_id("user_pass")

    print("Login")
    username_field.send_keys(username)
    password_field.send_keys(password)
    driver.find_element_by_id("wp-submit").click()
    try:
        driver.find_element_by_id("login_error")
        print("Login, Error. Account limited for 15 min")
        return
    except:
        pass

    driver.get("https://www.profitaccumulator.co.uk/oddsmatching/")
    # driver.get("https://www.profitaccumulator.co.uk/oddsmatching-free/")

    while True:
        time.sleep(5)
        try:
            driver.switch_to.frame(driver.find_element_by_id("matchoddsiframe"))
            WebDriverWait(driver, delay).until(
                EC.presence_of_element_located((By.XPATH, "//table[@id='tableBase']/tbody")))


            print("Getting odds")
            elements = driver.find_elements_by_xpath("//table[@id='tableBase']/tbody/tr")
            for tr in elements:
                rating = tr.find_element_by_xpath("td[contains(@class, 'rating')]").text
                backodds = tr.find_element_by_xpath("td[contains(@class, 'backOdds')]").text

                if float(rating) > rating_limit and float(backodds) < backodds_limit:
                    odds_found.append("Update: Bet with a rating of {} and back odds of {}".format(rating, backodds))
            if odds_found:
                # sendsms(odds_found)
                print(odds_found)
            odds_found = []

            time.sleep(update_delay)
            print("Reloading")
            driver.switch_to_default_content
            driver.refresh()

        except WebDriverException as e:  # Proxy not working
            print(e)
            print("Exception Hit")


main(username, password)
