import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options as FirefoxOptions

BROWSERSTACK_USERNAME = "chavavenkatapava_f7v2Nj"
BROWSERSTACK_ACCESS_KEY = "ApmeL5YXjmkbyXX1gybK"


# Function for local execution
def run_test_locally():
    # service = Service(executable_path='./chromedriver-win64/chromedriver.exe')
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment for headless mode
    driver = webdriver.Chrome()

    try:
        driver.get("https://elpais.com")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".b-t_d._g._g-xs.b_cnb-lg.b_row-2.b-t_d-6"))
        )
        print("Local Test Passed: elpais.com loaded successfully.")
    except Exception as e:
        print(f"Local Test Failed: {e}")
    finally:
        driver.quit()


# Function for BrowserStack execution
def run_test_on_browserstack(config):
    browser_options = None

    if config["browser"] == "Chrome":
        browser_options = Options()
    elif config["browser"] == "Firefox":
        browser_options = FirefoxOptions()
    elif config["browser"] == "Safari":
        browser_options = Options()

    # Add capabilities
    browser_options.set_capability("bstack:options", {
        "os": config["os"],
        "osVersion": config["os_version"],
        "sessionName": config["test_name"],
        "buildName": "Cross-Browser Testing Build"
    })
    browser_options.set_capability("browserName", config["browser"])
    browser_options.set_capability("browserVersion", config["browser_version"])

    try:
        driver = webdriver.Remote(
            command_executor=f"https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}@hub-cloud.browserstack.com"
                             f"/wd/hub",
            options=browser_options,
        )
    except Exception as e:
        print(e)

    try:
        driver.get("https://elpais.com")
        driver.implicitly_wait(20)
        accept_button = driver.find_element(By.ID, "didomi-notice-agree-button")
        ActionChains(driver).move_to_element(accept_button).perform()
        # Click the button
        accept_button.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".b_row.b_row-o._g._g-xs.b_row-2.b_el-4.b_row-4-md"))
        )
        opinion_section = driver.find_element(By.CSS_SELECTOR, ".b_row.b_row-o._g._g-xs.b_row-2.b_el-4.b_row-4-md")
        # opinion_section.click()

        articles = opinion_section.find_elements(By.TAG_NAME, "article")
        # articles = []
        for article in articles:
            try:
                print(article)
                title = article.find_element(By.TAG_NAME, "h2").text
                link = article.find_element(By.TAG_NAME, "a").get_attribute("href")
                # link.click()
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(link)
                driver.implicitly_wait(10)
                content = driver.find_element(By.CSS_SELECTOR, "article").text

                image = ""
                try:
                    image_element = driver.find_element(By.CSS_SELECTOR, "figure img")
                    image = image_element.get_attribute("src")
                except NoSuchElementException:
                    image = "Image not found"

                articles_data.append({
                    "title": title,
                    "content": content,
                    "image": image
                })

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            except Exception as e:
                print(f"Error fetching article data: {e}")
        print(f"Test Passed on {config['browser']} ({config['os']}): elpais.com loaded successfully.")
    except Exception as e:
        print(f"Test Failed on {config['browser']} ({config['os']}): {e}")
    finally:
        driver.quit()


def main():
    # Run local test
    print("Running Local Test...")
    run_test_locally()

    # BrowserStack configurations
    configs = [
        {"os": "Windows", "os_version": "10", "browser": "Chrome", "browser_version": "latest",
         "test_name": "Windows-Chrome"},
        {"os": "OS X", "os_version": "Ventura", "browser": "Safari", "browser_version": "latest",
         "test_name": "Mac-Safari"},
        {"os": "Windows", "os_version": "10", "browser": "Firefox", "browser_version": "latest",
         "test_name": "Windows-Firefox"},
        {"os": "Android", "os_version": "11.0", "browser": "Chrome", "browser_version": "latest",
         "test_name": "Android-Chrome"},
        {"os": "iOS", "os_version": "14", "browser": "Safari", "browser_version": "latest", "test_name": "iOS-Safari"},
    ]

    # Run tests on BrowserStack in parallel
    print("Running BrowserStack Tests...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(run_test_on_browserstack, configs)


if __name__ == "__main__":
    main()
