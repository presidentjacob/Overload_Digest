from bs4 import BeautifulSoup
import time, random, logging, re
from urllib.parse import urljoin
from article import Article
from config import header, separator
from utils import open_driver, get_response
from scraper.base import read_robots_txt
import queue
import datetime

def bbc(url):
    logging.info(f'Fetching {url}')
    # Get a response from BBC
    response = get_response(url)

    # If response status code is not 200, return
    if response.status_code != 200:
        print(f'{response.status_code}')
        return None
    
    soup = BeautifulSoup(response.text, 'lxml')

    # Find all information regarding file
    header_div = soup.find('h1', class_=re.compile(r'sc-.*'))
    time_tag = soup.find('time')
    author_span = soup.find('span', class_=re.compile(r'sc-.*lasLGY'))
    paragraphs = soup.find_all('p', class_=re.compile(r'sc-.*hxuGS'))

    if not header_div or not paragraphs:
        logging.info('No paragraphs found, skipping article')
        return None
    
    bbc_article = Article('BBC')
    full_article = ''

    if header_div:
        setattr(bbc_article, 'header', header_div.text.strip())
    
    if time_tag and time_tag.has_attr('datetime'):
        time = time_tag['datetime']
        time = datetime.datetime.fromisoformat(time).strftime('%Y-%m-%d %H:%M')
        setattr(bbc_article, 'time', time + '\n')

    if author_span:
        setattr(bbc_article, 'author', author_span.text.strip() + '\n')

    if paragraphs:
        for paragraph in paragraphs:
            paragraph_text = paragraph.get_text(separator=' ', strip=True)
            full_article += paragraph_text + '\n\n'
        full_article += separator
        setattr(bbc_article, 'paragraphs', full_article)

    return bbc_article

def bbc_grabber(url, text_widget, update_queue):
    logging.info(f'Fetching {url}')
    # Get a response from BBC
    response = get_response(url)

    # If response status code is not 200, return
    if response.status_code != 200:
        print(f'{response.status_code}')
        return None
    
    rp = read_robots_txt(url)
    crawl_delay = rp.crawl_delay(header['User-Agent'])
    # Create a soup from response
    # html = open_driver(url)

    soup = BeautifulSoup(response.text, 'lxml')

    # Find all links to articles
    links_div = soup.find_all('div', attrs={'data-testid': 'anchor-inner-wrapper'})
    seen_urls = set()

    # If links exist
    if links_div:
        for div in links_div:
            for link in div.find_all('a', href=True):
                # Get the link
                try:
                    href = link.get('href')
                except Exception as e:
                    logging.error(f'{e}')
                    continue

                if 'article' not in href:
                    continue
                if href.startswith('/'):
                    href = urljoin(url, href)

                if href not in seen_urls and rp.can_fetch(header['User-Agent'], href):
                    seen_urls.add(href)

                    # Wait between 3-15 seconds to look human
                    time.sleep(crawl_delay if crawl_delay else random.randint(3, 15))

                    article = bbc(href)
                    
                    if article:
                        update_queue.put((text_widget, article.__str__()))

    return