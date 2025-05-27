from bs4 import BeautifulSoup
import time, random, logging
from article import Article
from config import header, separator
from utils import get_response
from scraper.base import read_robots_txt

# Define npr
def npr(url):
    logging.info(f'Fetching {url}')
    # Exception handling, return nothing if Fox freezes
    response = get_response(url)
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, 'lxml')
    
    # Find all information in article
    header_div = soup.find('div', class_='storytitle')
    headline = header_div.find('h1') if header_div else None
    author_p = soup.find('p', class_='byline__name byline__name--block')
    time_div = soup.find('div', class_='dateblock')
    paragraph_div = soup.find('div', {'id': 'storytext'})

    # Return if missing important content
    if not header_div or not paragraph_div:
        logging.info('No paragraphs found, skipping article')
        return None

    npr_article = Article('NPR')
    full_article = ''

    # Find and insert all content into npr_article
    if headline and paragraph_div:
        setattr(npr_article, 'header', headline.text.strip())

    if author_p and paragraph_div:
        setattr(npr_article, 'author', f'{author_p.text.strip()}\n')

    # Take both the date and time of the article, located in two different spans
    if time_div and paragraph_div:
        date_span = time_div.find('span', class_='date')
        time_span = time_div.find('span', class_='time')

        date_text = date_span.text.strip() if date_span else ''
        time_text = date_span.text.strip() if time_span else ''

        setattr(npr_article, 'time', f'{date_text}, {time_text}')

    # Take the paragraph and remove any links in the text
    if paragraph_div:
        for paragraph in paragraph_div:
            paragraph_text = paragraph.get_text(separator=' ', strip=True)
            full_article += paragraph_text +'\n'
        full_article += separator
        setattr(npr_article, 'paragraphs', full_article)

    return npr_article

# Define npr_grabber
def npr_grabber(url, text_widget, update_queue):
    logging.info(f'Fetching {url}')
    response = get_response(url)

    if response.status_code != 200:
        return None
    
    rp = read_robots_txt(url)
    crawl_delay = rp.crawl_delay(header['User-Agent'])

    # Setup a readable text
    soup = BeautifulSoup(response.text, 'lxml')

    # Find all links to articles
    links_div = soup.find_all('div', class_='story-text')

    seen_urls = set()

    # Search through the links_div to get each article from npr
    if links_div:
        for link in links_div:
            for found_link in link.find_all('a', href=True):
                href = found_link.get('href')
                if href not in seen_urls and rp.can_fetch(header['User-Agent'], href):
                    seen_urls.add(href)

                    # Wait between 3-15 seconds to look like human activity
                    time.sleep(crawl_delay if crawl_delay else random.randint(3, 15))

                    article = npr(href)

                    if article:
                        update_queue.put((text_widget, article.__str__()))
                    
    return