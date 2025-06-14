import requests, logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from config import header
from screeninfo import get_monitors

def open_driver(url):
    # Setup a headless driver
    options = Options()
    options.add_argument('--headless')
    # Disable blink features to make it look like a user
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent={}'.format(header['User-Agent']))
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    WebDriverWait(driver, 5)
    html = driver.page_source
    driver.quit()
    return html

def get_response(url):
    try:
        response = requests.get(url, headers=header, timeout=10)
        logging.info(f'Fetched {url} with status code {response.status_code}')
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f'Error fetching {url}: {e}')
        return None

def screen_info():
    # Get screen information
    monitors = {}

    for num, m in enumerate(get_monitors()):
        monitors[num] = {
            'width': m.width,
            'height': m.height,
        }

    logging.info(f'Screen information: {monitors}')
    return monitors

def scrape_and_print(scraper_function, url, text_widget, update_queue):
    scraper_function(url, text_widget, update_queue)