import requests
import textwrap
import tkinter as tk
from tkinter import ttk, scrolledtext, font, Label
from bs4 import BeautifulSoup
import threading
import queue
import time
import random
import urllib.robotparser
from urllib.parse import urljoin
import re
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Setup an article class to contain article information
class Article:
    def __init__(self, source):
        self.source = source
        self.header = ''
        self.subheader = ''
        self.author = ''
        self.time = ''
        self.paragraphs = ''
    def __str__(self):
        return f'\n{self.source}\n\n{self.header}\n{self.subheader}\n{self.author}\n{self.time}\n{self.paragraphs}'


# Use headers to make it look as if program is a user and not a bot
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Referer': 'http://www.google.com/',
    'Upgrade-Insecure-Requests': '1',
}

# Separator between articles
separator = '-' * 77

# Setup queue for each article to be scraped
update_queue = queue.Queue()

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
        return response
    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')
        return None

# Update the gui, and recursively update
def update_gui(window):
    try:
        while True:
            # Take the queue content and insert in the widget
            widget, text = update_queue.get_nowait()
            widget.config(state='normal')
            widget.insert('end', text)
            widget.config(state='disable')
    except queue.Empty:
        pass

    window.after(10, update_gui, window)

# Define auto_scroll
def auto_scroll(text_widget):
    # Set each to scroll at the exact same speed
    total_lines = int(text_widget.index('end-1c').split('.')[0])
    speed = .02 / total_lines
    current_position = text_widget.yview()[0]

    # Reset position to the top if the autoscroll reaches the bottom.
    if current_position < 1:
        text_widget.yview_moveto(current_position + speed)
        text_widget.after(50, lambda: auto_scroll(text_widget))
    else:
        text_widget.yview_moveto(0.0)
        text_widget.after(50, lambda: auto_scroll(text_widget))

# def print_paragraph(text):
#     line_length = 70
#     wrapped_text = textwrap.fill(text, line_length)
#     return wrapped_text

# Function for threading
def scrape_and_print(function, url, widget):
        function(url, widget)

def read_robots_txt(url):
    rp = urllib.robotparser.RobotFileParser()
    robots_url = urljoin(url, '/robots.txt')
    try:
        # Read robots.txt and return rp
        rp.set_url(robots_url)
        rp.read()
        return rp
    except Exception as e:
        print(f'Error reading robots.txt: {e}')
        return None

# Define CNN grabber
def CNN(url):
    response = get_response(url)
    
    if response.status_code != 200:
        print(f'Error: {response.status_code}')
        return None

    html = open_driver(url)

    # Parse into soup as lxml
    soup = BeautifulSoup(html, 'lxml')

    # Get all information regarding file
    header_div = soup.find('div', class_='headline__wrapper')
    headline = header_div.find('h1') if header_div else None
    subheader = header_div.find('h2') if header_div else None
    author_div = soup.find('div', class_='byline__names vossi-byline__names')
    time_div = soup.find('div', class_='timestamp vossi-timestamp')
    paragraph_div = soup.find('div', class_='article__content')

    # Create a new article
    cnn_article = Article('CNN')
    full_article = ''

    if not paragraph_div:
        return None

    # Only add information to the article class only if paragraph_div exists
    # If there are no paragraphs, the article will not be added.
    if headline and paragraph_div:
        setattr(cnn_article, 'header', headline.text.strip())

    if subheader and paragraph_div:
        setattr(cnn_article, 'subheader', subheader.text.strip() + '\n')

    if author_div and paragraph_div:
        authors = [authors.text.strip() for authors in soup.find_all('span', class_='byline__name')]
        setattr(cnn_article, 'author', ', '.join(authors) + '\n')

    if time_div and paragraph_div:
        time = time_div.text
        time = time.replace('Updated', '')
        time = time.replace('Published', '')
        setattr(cnn_article, 'time', time.strip() + '\n')

    if paragraph_div:
        for paragraph in paragraph_div.find_all('p'):
            full_article += (paragraph.text.strip() +'\n\n')
        full_article += separator
        setattr(cnn_article, 'paragraphs', full_article)

    return cnn_article

# Define a grabber for CNN.com
def CNN_grabber(url, text_widget):
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
                print(f'Error: {e}')
                continue
            
            href = found_link.get('href')
            if href.startswith('/'):
                href = urljoin(url, href)

            # Improve runtime and make sure articles are not read twice and respect robots.txt
            if href not in seen_urls or rp.can_fetch(header['User-Agent'], href):
                seen_urls.add(href)

                # Wait between 3-15 seconds to look human
                time.sleep(crawl_delay if crawl_delay else random.randint(3,15))
                article = CNN(href)

                if article:
                    update_queue.put((text_widget, article.__str__()))
    return

def fox(url):
    # Exception handling, return nothing if Fox freezes
    response = get_response(url)
    
    if response.status_code != 200:
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
def fox_grabber(url, text_widget):
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

# Define npr
def npr(url):
    # Exception handling, return nothing if Fox freezes
    response = get_response(url)
    if response.status_code != 200:
        print(f'Error: {response.status_code}')
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
def npr_grabber(url, text_widget):
    response = get_response(url)

    if response.status_code != 200:
        print(f'Error: {response.status_code}')
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

def techcrunch(url):
    response = get_response(url)
    
    if response.status_code != 200:
        print(f'Error: {response.status_code}')
        return None
    
    html = open_driver(url)
    # Create soup
    soup = BeautifulSoup(html, 'lxml')
    
    # Find all information in article
    headline = soup.find('h1', class_='article-hero__title wp-block-post-title')
    author_a = soup.find('a', class_='wp-block-tc23-author-card-name__link')
    time_time = soup.find('time', class_='datetime')
    paragraphs_p = soup.find_all('p', class_='wp-block-paragraph')

    if not headline or not paragraphs_p:
        return None

    techcrunch_article = Article('TECHCRUNCH')
    full_article = ''

    if headline:
        setattr(techcrunch_article, 'header', (headline.text.strip()))
    
    if author_a:
        setattr(techcrunch_article, 'author', author_a.text.strip())

    if time_time:
        setattr(techcrunch_article, 'time', time_time.text.strip())

    if paragraphs_p:
        for paragraphs in paragraphs_p:
            paragraph_text = paragraphs.get_text(separator=' ', strip=True)
            full_article += paragraph_text + '\n\n'
        full_article += separator
        setattr(techcrunch_article, 'paragraphs', full_article)

    return techcrunch_article


def techcrunch_grabber(url, text_widget):
    # Try to get a response from techcrunch
    response = get_response(url)

    if response.status_code != 200:
        print(f'Error: {response.status_code}')
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
                print(f'Error: {e}')
                continue

            if href not in seen_urls and rp.can_fetch(header['User-Agent'], href):
                seen_urls.add(href)
                time.sleep(crawl_delay if crawl_delay else random.randint(3, 15))

                article = techcrunch(href)

            if article:
                update_queue.put((text_widget, article.__str__()))
    
    return

def four_media(url):
    response = get_response(url)
    
    if response.status_code != 200:
        print(f'Error: {response.status_code}')
        return None
    
    # Create soup
    soup = BeautifulSoup(response.text, 'lxml')

    headline = soup.find('h1', class_='post-hero__title').text

    # Try to find a subheadline
    try:
        subheadline = soup.find('div', class_='post-hero__excerpt').text
    except Exception:
        print(f'No subheader found')
    
    # Find the exact time text
    time = soup.find('time', class_='byline__date').text

    authors_byline = soup.find('div', class_='byline')
    paragraphs_div = soup.find('div', class_='post__content no-overflow')

    four_article = Article('404 MEDIA')

    if not headline or not paragraphs_div.text:
        return None

    if headline:
        setattr(four_article, 'header', headline.strip() + '\n')
    if subheadline:
        setattr(four_article, 'subheader', subheadline.strip() + '\n')
    if time:
        # Use regex to replace multiple spaces with just one space, then strip spaces at front
        setattr(four_article, 'time', re.sub(r'\s+', ' ', time).strip() + '\n')

    # Get every author
    if authors_byline:
        authors = [authors.text.strip() for authors in authors_byline.find_all('span')]
        all_authors = ', '.join(authors)
        all_authors = all_authors.replace(',,', '').replace('·', '').strip().rstrip(',') + '\n'
        setattr(four_article, 'author', all_authors)

    # Get every paragraph
    if paragraphs_div:
        paragraphs = [paragraphs.text.strip() for paragraphs in paragraphs_div.find_all('p')]
        setattr(four_article, 'paragraphs', '\n\n'.join(paragraphs) + f'\n{separator}')

    return four_article


def four_media_grabber(url, text_widget):
    # Try to get a response from techcrunch
    response = get_response(url)

    if response.status_code != 200:
        print(f'Error: {response.status_code}')
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
        print(f'Error: {e}')
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
                print(f'Error: {e}')
                continue

            if href.startswith('/'):
                href = urljoin(url, href)

            if href not in seen_urls and rp.can_fetch(header['User-Agent'], href):
                seen_urls.add(href)
                time.sleep(crawl_delay if crawl_delay else random.randint(3,15))

                article = four_media(href)

            if article:
                update_queue.put((text_widget, article.__str__()))

    return

def wired(url):
    # Try to get the url, if it fails, return None
    response = get_response(url)
    
    # Get and check the status code
    if response.status_code != 200:
        print(f'Error: {response.status_code}')
        return None
    
    html = open_driver(url)
    # Create a soup from response
    soup = BeautifulSoup(html, 'lxml')

    wired_article = Article('WIRED')

    # Find the headline information using regex as wired uses random classnames
    headline_h1 = soup.find('h1', class_=re.compile(r'BaseWrap.*'))
    subheader_div = soup.find('div', class_=re.compile(r'BaseWrap.*'))
    time = soup.find('time', class_=re.compile(r'SplitScreenContentHeaderPublishDate.*'))
    author_span = soup.find_all('span', class_=re.compile(r'BylineName.*byline__name'))
    paragraphs_div = soup.find('div', class_='body__inner-container')

    if headline_h1:
        headline = headline_h1.text.strip()
        setattr(wired_article, 'header', headline + '\n')
    
    if subheader_div:
        subheader = subheader_div.text.strip()
        setattr(wired_article, 'subheader', subheader + '\n')
    
    if time:
        time = time.text.strip()
        setattr(wired_article, 'time', time + '\n')

    if author_span:
        authors = [authors.text.strip() for authors in author_span]
        all_authors = ', '.join(authors)
        # all_authors = all_authors.replace(',,', '').replace('·', '').strip().rstrip(',') + '\n'
        setattr(wired_article, 'author', all_authors)

    if paragraphs_div:
        paragraphs = [paragraphs.text.strip() for paragraphs in paragraphs_div.find_all('p')]
        setattr(wired_article, 'paragraphs', '\n\n'.join(paragraphs) + f'\n{separator}')

    return wired_article


def wired_grabber(url, text_widget):
    # Get a response from wired
    response = get_response(url)

    # If response status code is not 200, return
    if response.status_code != 200:
        print(f'Error: {response.status_code}')
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
                print(f'Error: {e}')
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
    return

def bbc(url):
    # Get a response from BBC
    response = get_response(url)

    # If response status code is not 200, return
    if response.status_code != 200:
        print(f'Error: {response.status_code}')
        return None
    
    soup = BeautifulSoup(response.text, 'lxml')

    # Find all information regarding file
    header_div = soup.find('h1', class_=re.compile(r'sc-.*'))
    time_tag = soup.find('time')
    author_span = soup.find('span', class_=re.compile(r'sc-.*lasLGY'))
    paragraphs = soup.find_all('p', class_=re.compile(r'sc-.*hxuGS'))

    if not header_div or not paragraphs:
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

def bbc_grabber(url, text_widget):
    # Get a response from BBC
    response = get_response(url)

    # If response status code is not 200, return
    if response.status_code != 200:
        print(f'Error: {response.status_code}')
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
                    print(f'Error: {e}')
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

def cbs(url):
    # Get a response from BBC
    response = get_response(url)
    # If response status code is not 200, return
    try:
        if response.status_code != 200:
            print(f'Error: {response.status_code}')
            return None
    except Exception as e:
        print(f'Error: {e}')
        return None
    
    soup = BeautifulSoup(response.text, 'lxml')
    
    # Find all article content
    header_h1 = soup.find('h1', class_='content__title')
    authors = soup.find_all('span', class_=re.compile(r'byline__author*'))
    time = soup.find('time')
    paragraphs_section = soup.find('section', class_='content__body')

    if not header_h1 or not paragraphs_section or 'live updates' in header_h1.text:
        return None
    
    cbs_article = Article('CBS NEWS')
    if header_h1:
        setattr(cbs_article, 'header', header_h1.text.strip())
    
    if authors:
        authors = [author.text.strip() for author in authors]
        all_authors = ', '.join(authors)
        setattr(cbs_article, 'author', all_authors + '\n')
    
    if time and time.has_attr('datetime'):
        time = time['datetime']
        time = datetime.datetime.fromisoformat(time).strftime('%Y %m %d %H:%M')
        setattr(cbs_article, 'time', time + '\n')
    elif time:
        time = time.text.strip()
        time = time.replace('Updated on: ', '')
        setattr(cbs_article, 'time', time + '\n')

    if paragraphs_section:
        paragraphs = [paragraphs.text.strip() for paragraphs in paragraphs_section.find_all('p')]
        setattr(cbs_article, 'paragraphs', '\n\n'.join(paragraphs) + f'\n{separator}')

    return cbs_article

def cbs_grabber(url, text_widget):
    # Get a response from BBC
    response = get_response(url)

    # If response status code is not 200, return
    if response.status_code != 200:
        print(f'Error: {response.status_code}')
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
                print(f'Error: {e}')
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
    return

def abc(url):
    # Get a response from ABC
    response = get_response(url)

    # If response status code is not 200, return
    if response.status_code != 200:
        print(f'Error: {response.status_code}')
        return None
    
    soup = BeautifulSoup(response.text, 'lxml')
    print(soup.prettify())

def abc_grabber(url, text_widget):
    # Get a response from ABC
    response = get_response(url)

    # If response status code is not 200, return
    if response.status_code != 200:
        print(f'Error: {response.status_code}')
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
                print(f'Error: {e}')
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

def main():
    # Political News
    cnn_url = 'https://www.cnn.com'
    fox_url = 'https://www.foxnews.com'
    npr_url = 'https://www.npr.org'
    bbc_url = 'https://www.bbc.com'
    cbs_url = 'https://www.cbsnews.com'
    abc_url = 'https://abcnews.go.com'
    # Tech News
    techcrunch_url = 'https://techcrunch.com'
    four_zero_four_media_url = 'https://www.404media.co'
    wired_url = 'https://www.wired.com'


    # Create main window
    window = tk.Tk()
    window.title('Overload Digest')
    window.geometry('640x480')
    window.configure(background='black')
    window.state('zoomed')

    # Create title headline on Overload Digest
    # T1 = tk.Text(window, bg='black', fg='gray50', insertbackground='white', cursor='arrow')
    # T1.tag_configure('center', justify='center', font=('Times New Roman', 50))
    # T1.insert('1.0', 'OVERLOAD DIGEST')
    # T1.tag_add('center', '1.0', 'end')
    # T1.config(state='disable')
    # T1.pack(side='top', fill='x', padx=20, pady=(20,5))

    # T2 = tk.Text(window, bg='black', fg='gray45', insertbackground='white', cursor='arrow')
    # T2.tag_configure('center', justify='center', font=('Times New Roman', 35))
    # T2.insert('1.0', 'NEWS DOESN\'T GET WORSE THAN THIS')
    # T2.tag_add('center', '1.0', 'end')
    # T2.config(state='disable')
    # T2.pack(side='top', fill='x', padx=20, pady=(5,20))

    T1 = tk.Label(window, text='オーバーロード・ダイジェスト', bg='black', fg='gray50', font=('MS Gothic', 35))
    T1.pack(side='top', fill='x')
    T2 = tk.Label(window, text='OVERLOAD DIGEST', bg='black', fg='gray50', font=('Fixedsys', 35))
    T2.pack(side='top', fill='x')
    T3 = tk.Label(window, text='超载摘要', bg='black', fg='gray50', font=('Microsoft YaHei', 35))
    T3.pack(side='top', fill='x')

    frame = tk.Frame(window, bg='black')
    frame.pack(fill='both', expand=True)

    # Define a scrollbar for user to scroll through information
    scrollbar = tk.Scrollbar(frame, orient='vertical')
    text_widgets = []

    # Setup text widgets for articles to be inserted.
    for i in range(3):
        text = tk.Text(frame, wrap='word', bg='black', fg='white', insertbackground='white', cursor='arrow',
                       yscrollcommand=scrollbar.set, font=('Fixedsys', 16))
        text.grid(row=0, column=i, sticky='nsew', padx = 10, pady=10)
        text.config(state='disable')
        text_widgets.append(text)
        auto_scroll(text)

    # Configure column resizing
    for i in range(3):
        frame.columnconfigure(i, weight=1)
    frame.rowconfigure(0, weight=1)

    # CNN_grabber(cnn_url, text_widgets[0])
    # fox_grabber(fox_url, text_widgets[1])
    # npr_grabber(npr_url, text_widgets[2])

    # Run threads to update per each article scraped.
    # threading.Thread(target=scrape_and_print, args=(CNN_grabber, cnn_url, text_widgets[0],)).start()
    # threading.Thread(target=scrape_and_print, args=(fox_grabber, fox_url, text_widgets[0],)).start()
    # threading.Thread(target=scrape_and_print, args=(npr_grabber, npr_url, text_widgets[0],)).start()

    # threading.Thread(target=scrape_and_print, args=(techcrunch_grabber, techcrunch_url, text_widgets[1],)).start()
    # threading.Thread(target=scrape_and_print, args=(four_media_grabber, four_zero_four_media_url, text_widgets[1],)).start()
    # threading.Thread(target=scrape_and_print, args=(wired_grabber, wired_url, text_widgets[1],)).start()

    # threading.Thread(target=scrape_and_print, args=(bbc_grabber, bbc_url, text_widgets[2],)).start()
    # threading.Thread(target=scrape_and_print, args=(cbs_grabber, cbs_url, text_widgets[2],)).start()
    threading.Thread(target=scrape_and_print, args=(abc_grabber, abc_url, text_widgets[2],)).start()

    window.after(15, update_gui, window)

    time.sleep(20)

    # Disable configuration so user cannot type in widget
    # for widget in text_widgets:
    #     widget.config(state='disable')

    # Initialize window
    window.mainloop()

main()