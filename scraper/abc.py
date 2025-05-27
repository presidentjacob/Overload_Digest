from bs4 import BeautifulSoup
import time, random, logging, re
from urllib.parse import urljoin
from article import Article
from config import header, separator
from utils import open_driver, get_response
from scraper.base import read_robots_txt
import queue
import datetime

def abc(url):
    logging.info(f'Fetching {url}')
    # Get a response from ABC
    response = get_response(url)

    # If response status code is not 200, return
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, 'lxml')
    
    # Find all information
    header_h1 = soup.find('h1')
    subheader_h2 = soup.find('div', attrs={'data-testid': 'prism-article-body'}).find('h2')
    authors = soup.find_all('a', attrs={'data-testid': 'prism-linkbase'})
    # Work on time div later, too difficult to find it right now
    
    paragraphs_p = soup.find_all('p')

    if not header_h1 or not paragraphs_p:
        logging.info('No paragraphs found, skipping article')
        return None
    
    abc_article = Article('ABC NEWS')
    full_article = ''

    if header_h1:
        setattr(abc_article, 'header', header_h1.text.strip())

    if subheader_h2:
        setattr(abc_article, 'subheader', subheader_h2.text.strip() + '\n')

    if authors:
        authors_array = []
        for a in authors:
            if a.find('h3') or a.find('h2') or a.find('a'):
                break
            authors_array.append(a.text.strip())
        all_authors = ', '.join(authors_array)
        setattr(abc_article, 'author', all_authors + '\n')
    

    if paragraphs_p:
        for paragraph in paragraphs_p:
            paragraph_text = paragraph.get_text(separator=' ', strip=True)
            full_article += paragraph_text + '\n\n'
        full_article += separator
        setattr(abc_article, 'paragraphs', full_article)
    
    return abc_article
    
def abc_grabber(url, text_widget, update_queue):
    logging.info(f'Fetching {url}')
    # Get a response from ABC
    response = get_response(url)

    # If response status code is not 200, return
    if response.status_code != 200:
        return None
    
    rp = read_robots_txt(url)
    crawl_delay = rp.crawl_delay(header['User-Agent'])
    # Create a soup from response
    soup = BeautifulSoup(response.text, 'lxml')

    # Find all links to articles
    links_div = soup.find_all('div', class_=re.compile(r'^[a-zA-Z]+ *'))
    seen_urls = set()

    if links_div:
        for link in links_div:
            # Get the link
            try:
                href = link.find('a', href=True).get('href')
            except Exception as e:
                logging.error(f'{e}')
                continue

            if href.startswith('/'):
                href = urljoin(url, href)

            if href not in seen_urls and rp.can_fetch(header['User-Agent'], href) and 'story' in href:
                seen_urls.add(href)

                # Wait between 3-15 seconds to look human
                time.sleep(crawl_delay if crawl_delay else random.randint(3, 15))

                article = abc(href)
                
                if article:
                    update_queue.put((text_widget, article.__str__()))
    print('done')
    return