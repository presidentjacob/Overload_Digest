from bs4 import BeautifulSoup
import time, random, logging, re
from urllib.parse import urljoin
from article import CBSArticle as Article
from config import header, separator
from utils import get_response
from scraper.base import read_robots_txt
import datetime

def cbs(url):
    logging.info(f'Fetching {url}')
    # Get a response from BBC
    response = get_response(url)
    # If response status code is not 200, return
    try:
        if response.status_code != 200:
            return None
    except Exception as e:
        logging.error(f'{e}')
        return None
    
    soup = BeautifulSoup(response.text, 'lxml')
    
    # Find all article content
    header_h1 = soup.find('h1', class_='content__title')
    authors = soup.find_all('span', class_=re.compile(r'byline__author*'))
    time = soup.find('time')
    paragraphs_section = soup.find('section', class_='content__body')

    if not header_h1 or not paragraphs_section or 'live updates' in header_h1.text:
        return None
    
    cbs_article = Article()
    if header_h1:
        cbs_article.set_header(header_h1.text.strip())
    
    if authors:
        authors = [author.text.strip() for author in authors]
        all_authors = ', '.join(authors)
        cbs_article.set_author(all_authors)
    
    if time and time.has_attr('datetime'):
        time = time['datetime']
        time = datetime.datetime.fromisoformat(time).strftime('%Y %m %d %H:%M')
        cbs_article.set_time(time)
    elif time:
        time = time.text.strip()
        time = time.replace('Updated on: ', '')
        cbs_article.set_time(time)

    if paragraphs_section:
        for paragraph in paragraphs_section.find_all('p'):
            paragraph_text = paragraph.get_text(separator=' ', strip=True)
            cbs_article.set_paragraphs(paragraph_text.strip())

    return cbs_article

def cbs_grabber(url, text_widget, update_queue):
    logging.info(f'Fetching {url}')
    # Get a response from BBC
    response = get_response(url)

    # If response status code is not 200, return
    if response.status_code != 200:
        return None
    
    rp = read_robots_txt(url)
    crawl_delay = rp.crawl_delay(header['User-Agent'])
    # Create a soup from response
    
    # html = open_driver(url)

    soup = BeautifulSoup(response.text, 'lxml')
    links_article = soup.find_all('article', class_=re.compile(r'item.*'))
    seen_urls = set()

    if links_article:
        for link in links_article:
            # Get the link
            try:
                href = link.find('a', href=True).get('href')
            except Exception as e:
                logging.error(f'{e}')
                continue

            if href.startswith('/'):
                href = urljoin(url, href)
            
            if href not in seen_urls and rp.can_fetch(header['User-Agent'], href):
                seen_urls.add(href)

                # Wait between 3-15 seconds to look human
                time.sleep(crawl_delay if crawl_delay else random.randint(3, 15))

                article = cbs(href)
                
                if article:
                    update_queue.put((text_widget, article.__str__()))
                    logging.info(article.logging_info())
    return