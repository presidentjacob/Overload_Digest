from bs4 import BeautifulSoup
import time, random, logging, re
from urllib.parse import urljoin
from article import Article
from config import header, separator
from utils import get_response
from scraper.base import read_robots_txt

# Define Fox for scraping
def fox(url):
    logging.info(f'Fetching {url}')
    # Exception handling, return nothing if Fox freezes
    response = get_response(url)
    
    try:
        if response.status_code != 200:
            return None
    except Exception as e:
        return None

    soup = BeautifulSoup(response.text, 'lxml')    
    # Parse into soup as lxml
    # soup = BeautifulSoup(response.text, 'lxml')

    header_div = soup.find('div', class_='article-meta article-meta-upper')
    headline = header_div.find('h1') if header_div else None
    subheader = header_div.find('h2') if header_div else None
    author_div = soup.find('div', class_='author-byline')
    date_span = soup.find('span', class_='article-date')
    paragraph_p = soup.find_all('p')

    fox_article = Article('Fox News')
    full_article = ''

    # Return if missing important content
    if not header_div or not paragraph_p:
        logging.info('No paragraphs found, skipping article')
        return None
    
    # Only add information to the article class only if paragraph_div exists
    # If there are no paragraphs, the article will not be added.
    if headline and paragraph_p:
        setattr(fox_article, 'header', (headline.text.strip()))

    if subheader and paragraph_p:
        setattr(fox_article, 'subheader', subheader.text.strip() + '\n')

    # No clue what lambda does but this is the only way to get it working

    if author_div and paragraph_p:
        author_link = author_div.find('a', href=lambda href: href and '/person/' in href)
        if author_link:
            author_name = author_link.text.strip()
            setattr(fox_article, 'author', author_name + '\n')

    if date_span and paragraph_p:
        time_tag = date_span.find('time')
        if time_tag:
            time = time_tag.text.strip()
            setattr(fox_article, 'time', time + '\n')

    if paragraph_p:
        for paragraph in paragraph_p:
            paragraph_text = paragraph.get_text(separator=' ', strip=True)
            if 'FOX News' not in paragraph and 'subcribed to' not in paragraph_text:
                formatted_paragraph = paragraph_text
                full_article += formatted_paragraph + '\n\n'
        full_article += separator
        setattr(fox_article, 'paragraphs', full_article)
    
    return fox_article

# Define fox_grabber
def fox_grabber(url, text_widget, update_queue):
    logging.info(f'Fetching {url}')
    response = get_response(url)
    https = 'https:'

    # If no response return
    if response.status_code != 200:
        return None
    
    rp = read_robots_txt(url)
    crawl_delay = rp.crawl_delay(header['User-Agent'])

    # Parse all html text as lxml
    soup = BeautifulSoup(response.text, 'lxml')

    # Find all links to articles
    all_links = soup.find_all('header', class_=('info-header'))

    # If links exist
    if all_links:
        # For all found
        for links in all_links:
            # Find 'a' who's href is true
            for link in links.find_all('a', href=True):
                href = link.get('href')
                if href.startswith('/'):
                        href = urljoin(https, href)
                # Ignore anything that isn't news
                if rp.can_fetch(header['User-Agent'], href):
                    # Wait between 3-15 seconds to look human
                    time.sleep(crawl_delay if crawl_delay else random.randint(3, 15))

                    article = fox(href)

                    if article:
                        update_queue.put((text_widget, article.__str__()))

    return