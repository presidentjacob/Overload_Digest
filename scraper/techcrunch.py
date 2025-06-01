from bs4 import BeautifulSoup
import time, random, logging
from article import TechCrunchArticle as Article
from config import header, separator
from utils import open_driver, get_response
from scraper.base import read_robots_txt

# Define techcrunch
def techcrunch(url):
    logging.info(f'Fetching {url}')
    response = get_response(url)
    
    try:
        if response.status_code != 200:
            return None
    except Exception as e:
        logging.error(f'{e}')
    
    html = open_driver(url)
    # Create soup
    soup = BeautifulSoup(html, 'lxml')
    
    # Find all information in article
    headline = soup.find('h1', class_='article-hero__title wp-block-post-title')
    author_a = soup.find('a', class_='wp-block-tc23-author-card-name__link')
    time_time = soup.find('time', class_='datetime')
    paragraphs_p = soup.find_all('p', class_='wp-block-paragraph')

    if not headline or not paragraphs_p:
        logging.info('No paragraphs found, skipping article')
        return None

    techcrunch_article = Article('TECHCRUNCH')

    if headline:
        techcrunch_article.set_header(headline.text.strip())
    
    if author_a:
        authors = [author.text.strip() for author in author_a.find_all('span', class_='byline__name')]
        all_authors = ', '.join(authors)
        techcrunch_article.set_author(all_authors)

    if time_time:
        techcrunch_article.set_time(time_time.text.strip())

    if paragraphs_p:
        for paragraphs in paragraphs_p:
            paragraph_text = paragraphs.get_text(separator=' ', strip=True)
            techcrunch_article.set_paragraphs(paragraph_text.strip())

    return techcrunch_article

# Define techcrunch_grabber
def techcrunch_grabber(url, text_widget, update_queue):
    logging.info(f'Fetching {url}')
    # Try to get a response from techcrunch
    response = get_response(url)

    if response.status_code != 200:
        return None
    
    # Get information from read robots
    rp = read_robots_txt(url)
    crawl_delay = rp.crawl_delay(header['User-Agent'])

    html = open_driver(url)

    # Setup readable text
    soup = BeautifulSoup(html, 'lxml')

    # Find all links to articls
    links_div = soup.find_all('div', class_='loop-card__content')
    seen_urls = set()

    if links_div:
        for link in links_div:
            found_h3 = link.find('h3', class_='loop-card__title')
            found_a = found_h3.find('a', href=True)
            # Some have a 'nonetype' and will throw an error 
            try:
                href = found_a.get('href')
            except Exception as e:
                logging.error(f'{e}')
                continue

            if href not in seen_urls and rp.can_fetch(header['User-Agent'], href):
                seen_urls.add(href)
                time.sleep(crawl_delay if crawl_delay else random.randint(3, 15))

                article = techcrunch(href)

                if article:
                    update_queue.put((text_widget, article.__str__()))
                    logging.info(article.logging_info())
    
    return