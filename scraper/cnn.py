from bs4 import BeautifulSoup
import time, random, logging, re
from urllib.parse import urljoin
from article import CNNArticle as Article
from config import header, separator
from utils import open_driver, get_response
from scraper.base import read_robots_txt

# Define CNN grabber
def cnn(url):
    logging.info(f'Fetching {url}')
    response = get_response(url)
    
    if response.status_code != 200:
        return None

    html = open_driver(url)

    # Parse into soup as lxml
    soup = BeautifulSoup(html, 'lxml')

    # Get all information regarding file
    header_div = soup.find('div', class_='headline__wrapper')
    headline = header_div.find('h1') if header_div else None
    author_div = soup.find('div', class_='byline__names vossi-byline__names')
    time_div = soup.find('div', class_='timestamp vossi-timestamp')
    paragraph_div = soup.find('div', class_='article__content')

    # Create a new article
    cnn_article = Article()

    if not paragraph_div:
        logging.info('No paragraphs found, skipping article')
        return None

    # Only add information to the article class only if paragraph_div exists
    # If there are no paragraphs, the article will not be added.
    if headline and paragraph_div:
        cnn_article.set_header(headline.text.strip())

    if author_div and paragraph_div:
        authors = [authors.text.strip() for authors in soup.find_all('span', class_='byline__name')]
        cnn_article.set_author(', '.join(authors))

    if time_div and paragraph_div:
        time = time_div.text
        time = time.replace('Updated', '')
        time = time.replace('Published', '')
        cnn_article.set_time(time.strip())

    if paragraph_div:
        for paragraph in paragraph_div.find_all('p'):
            paragraph_text = paragraph.get_text(separator=' ', strip=True)
            cnn_article.set_paragraphs(paragraph_text.strip())

    return cnn_article

# Define a grabber for CNN.com
def cnn_grabber(url, text_widget, update_queue):
    logging.info(f'Fetching {url}')
    response = get_response(url)

    # if no response return
    if response.status_code != 200:
        return None

    # Setup robots parser
    rp = read_robots_txt(url)
    crawl_delay = rp.crawl_delay(header['User-Agent'])

    html = open_driver(url)

    # Parse all text to lxml
    soup = BeautifulSoup(html, 'lxml')
    # Find all links to articles
    links_div = soup.find_all('div', class_=(re.compile(r'container__field-links*')))

    seen_urls = set()
    if links_div:
        for div in links_div:
            try:
                found_link = div.find('a', href=True)
            except Exception as e:
                logging.error(f'{e}')
                continue
            
            href = found_link.get('href')
            if href.startswith('/'):
                href = urljoin(url, href)

            # Improve runtime and make sure articles are not read twice and respect robots.txt
            if href not in seen_urls or rp.can_fetch(header['User-Agent'], href):
                seen_urls.add(href)

                # Wait between 3-15 seconds to look human
                time.sleep(crawl_delay if crawl_delay else random.randint(3,15))
                article = cnn(href)

                if article:
                    update_queue.put((text_widget, article.__str__()))
                    logging.info(article.logging_info())
    return