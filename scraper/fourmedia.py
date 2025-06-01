from bs4 import BeautifulSoup
import time, random, logging, re
from urllib.parse import urljoin
from article import FourZeroFourMediaArticle as Article
from config import header, separator
from utils import get_response
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from scraper.base import read_robots_txt

# Function to scrape 404 Media articles
def four_media(url):
    logging.info(f'Fetching {url}')
    response = get_response(url)
    
    if response.status_code != 200:
        return None
    
    # Create soup
    soup = BeautifulSoup(response.text, 'lxml')

    headline = soup.find('h1', class_='post-hero__title')

    # Try to find a subheadline
    try:
        subheadline = soup.find('div', class_='post-hero__excerpt').text
    except Exception:
        logging.error('No subheadline found')
    
    # Find the exact time text
    time = soup.find('time', class_='byline__date').text

    authors_byline = soup.find('div', class_='byline')
    paragraphs_div = soup.find('div', class_='post__content no-overflow')

    four_article = Article()

    if not headline or not paragraphs_div:
        logging.info('No paragraphs found, skipping article')
        return None

    if headline:
        four_article.set_header(headline.text.strip())
        
    if subheadline:
        four_article.set_subheader(subheadline.strip())

    if time:
        # Use regex to replace multiple spaces with just one space, then strip spaces at front
        four_article.set_time(re.sub(r'\s+', ' ', time).strip())

    # Get every author
    if authors_byline:
        authors = [authors.text.strip() for authors in authors_byline.find_all('span')]
        all_authors = ', '.join(authors)
        all_authors = all_authors.replace(',,', '').replace('·', '').strip().rstrip(',') + '\n'
        four_article.set_author(all_authors)

    # Get every paragraph
    if paragraphs_div:
        for paragraph in paragraphs_div.find_all('p'):
            paragraph_text = paragraph.get_text(separator=' ', strip=True)
            four_article.set_paragraphs(paragraph_text.strip())

    return four_article

# Function to grab 404 Media articles
def four_media_grabber(url, text_widget, update_queue):
    logging.info(f'Fetching {url}')
    # Try to get a response from techcrunch
    response = get_response(url)

    if response.status_code != 200:
        return None
    
    # Read the robots.txt file
    rp = read_robots_txt(url)
    crawl_delay = rp.crawl_delay(header['User-Agent'])

    # Use Selenium to click more articles
    # Nevermind this does work :3
    # Don't call open_driver, as we need to click the button
    driver_options = webdriver.ChromeOptions()
    driver_options.add_argument('--headless')
    driver = webdriver.Chrome(options=driver_options)
    driver.get(url)
    
    wait = WebDriverWait(driver, 5)
    button = wait.until(EC.element_to_be_clickable((By.ID, 'load-more-posts')))

    actions = ActionChains(driver)
    actions.move_to_element(button).perform()

    # Click the button to load more articles
    try:
        button.click()
        time.sleep(2)
    except Exception as e:
        print(f'{e}')
        driver.quit()
        return None

    # Create soup
    html = driver.page_source

    soup = BeautifulSoup(html, 'lxml')
    driver.quit()
    
    # Find all links
    links_div = soup.find_all('div', class_='post-card__content')
    seen_urls = set()

    # Check for links
    if links_div:
        for link in links_div:
            found_h4 = link.find('h4', class_='post-card__title')
            found_a = found_h4.find('a', href=True)
            # Exception handling for href
            try:
                href = found_a.get('href')
            except Exception as e:
                logging.error(f'{e}')
                continue

            if href.startswith('/'):
                href = urljoin(url, href)

            if href not in seen_urls and rp.can_fetch(header['User-Agent'], href):
                seen_urls.add(href)
                time.sleep(crawl_delay if crawl_delay else random.randint(3,15))

                article = four_media(href)

            if article:
                update_queue.put((text_widget, article.__str__()))
                logging.info(article.logging_info())
    return