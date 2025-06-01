from bs4 import BeautifulSoup
import time, random, logging, re
from urllib.parse import urljoin
from article import WiredArticle as Article
from config import header, separator
from utils import open_driver, get_response
from scraper.base import read_robots_txt

# Define wired to fetch content from a given URL
def wired(url):
    logging.info(f'Fetching {url}')
    # Try to get the url, if it fails, return None
    response = get_response(url)
    
    # Get and check the status code
    if response.status_code != 200:
        print(f'{response.status_code}')
        return None
    
    html = open_driver(url)
    # Create a soup from response
    soup = BeautifulSoup(html, 'lxml')

    wired_article = Article()

    # Find the headline information using regex as wired uses random classnames
    headline_h1 = soup.find('h1', class_=re.compile(r'BaseWrap.*'))
    subheader_div = soup.find('div', class_=re.compile(r'BaseWrap.*'))
    time = soup.find('time', class_=re.compile(r'SplitScreenContentHeaderPublishDate.*'))
    author_span = soup.find_all('span', class_=re.compile(r'BylineName.*byline__name'))
    paragraphs_div = soup.find('div', class_='body__inner-container')

    if headline_h1:
        wired_article.set_header(headline_h1.text.strip())
    
    if subheader_div:
        wired_article.set_header(subheader_div.text.strip())
    
    if time:
        wired_article.set_time(time.text.strip())

    if author_span:
        authors = [author.text.strip() for author in author_span]
        all_authors = ', '.join(authors)
        # all_authors = all_authors.replace(',,', '').replace('·', '').strip().rstrip(',') + '\n'
        wired_article.set_author(all_authors)

    if paragraphs_div:
        for paragraph in paragraphs_div.find_all('p'):
            paragraph_text = paragraph.get_text(separator=' ', strip=True)
            wired_article.set_paragraphs(paragraph_text.strip())

    return wired_article

# Define wired grabber to fetch articles from a given URL and update the text widget
def wired_grabber(url, text_widget, update_queue):
    logging.info(f'Fetching {url}')
    # Get a response from wired
    response = get_response(url)

    # If response status code is not 200, return
    if response.status_code != 200:
        return None
    
    rp = read_robots_txt(url)
    crawl_delay = rp.crawl_delay(header['User-Agent'])

    html = open_driver(url)

    # Create a soup from response
    soup = BeautifulSoup(html, 'lxml')

    # Find all links to articles
    links_div = soup.find_all('div', class_=re.compile(r'SummaryItemContent.*summary-item__content'))
    seen_urls = set()
    # If links exist
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

            if href not in seen_urls and rp.can_fetch(header['User-Agent'], href):
                seen_urls.add(href)

                # Wait between 3-15 seconds to look human
                time.sleep(crawl_delay if crawl_delay else random.randint(3, 15))

                article = wired(href)
                
                if article:
                    update_queue.put((text_widget, article.__str__()))
                    logging.info(article.logging_info())
    return