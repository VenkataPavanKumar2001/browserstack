import os

import requests
from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from googletrans import Translator
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.common.action_chains import ActionChains
import time
from deep_translator import GoogleTranslator
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_driver():
    # service = Service(executable_path='./chromedriver-win64/chromedriver-win64/chromedriver.exe')
    # chrome_options = Options()
    # # chrome_options.add_argument("--headless")  # Run in headless mode
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    # options = Options()
    #
    # # set the proxy address
    # proxy_server_ip = "http://47.251.122.81:8888"
    #
    # # add the address to Chrome options
    # options.add_argument(f"--proxy-server={proxy_server_ip}")

    driver = webdriver.Edge()
    return driver


def fetch_opinion_articles():
    driver = setup_driver()
    driver.get("https://elpais.com")
    articles_data = []
    # sleep(100000)
    time.sleep(20)

    try:
        accept_button = driver.find_element(By.ID, "didomi-notice-agree-button")
        ActionChains(driver).move_to_element(accept_button).perform()
        # Click the button
        accept_button.click()
        opinion_section = driver.find_element(By.CSS_SELECTOR, ".b_row.b_row-o._g._g-xs.b_row-2.b_el-4.b_row-4-md")
        # opinion_section.click()

        articles = opinion_section.find_elements(By.TAG_NAME, "article")[:5]
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
                # driver.back()
                # print(driver.current_url)
                # driver.implicitly_wait(20)
                # home_url = "https://elpais.com/"  # Replace with the correct homepage URL
                # current_url = driver.current_url
                # if current_url != home_url:
                #     driver.back()
                #     driver.implicitly_wait(20)
                # WebDriverWait(driver, 10).until(
                #     EC.presence_of_element_located((By.CSS_SELECTOR, ".b-t_d._g._g-xs.b_cnb-lg.b_row-2.b-t_d-6"))
                # )
            except Exception as e:
                print(f"Error fetching article data: {e}")
    except Exception as e:
        print(f"Error navigating to Opinion section: {e}")
    finally:
        driver.quit()

    return articles_data


def download_images(articles):
    os.makedirs("images", exist_ok=True)

    for i, article in enumerate(articles):
        image_url = article.get("image", "")
        if image_url:
            try:
                response = requests.get(image_url, stream=True)
                with open(f"images/article_{i + 1}.jpg", "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
            except Exception as e:
                print(f"Error downloading image for article {i + 1}: {e}")


def translate_titles(articles):
    translator = GoogleTranslator(source='es', target='en')
    translations = []

    for article in articles:
        try:
            title = article["title"]
            translated = translator.translate(title)
            translations.append(translated)
        except Exception as e:
            print(f"Error translating title: {e}")

    return translations


def analyze_headers(translations):
    words = [word.lower() for title in translations for word in title.split()]
    word_count = Counter(words)
    return {word: count for word, count in word_count.items() if count > 2}


def main():
    articles = fetch_opinion_articles()
    for article in articles:
        print(article["title"], article["content"])
    download_images(articles)

    translations = translate_titles(articles)
    print("Translated Titles:", translations)

    repeated_words = analyze_headers(translations)
    print("Repeated Words:", repeated_words)


if __name__ == "__main__":
    main()
