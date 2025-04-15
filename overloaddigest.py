import requests
import validators
import textwrap
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import tkinter.font as font
from tkinter import Label
from bs4 import BeautifulSoup
import threading
import queue
import time
import random
import urllib.robotparser
from urllib.parse import urljoin

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
        return f'\n\t\t\t\t{self.source}\n\n{self.header}\n{self.subheader}\n{self.author}\n{self.time}\n{self.paragraphs}'

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
    try:
        response = requests.get(url, timeout=.5)
        soup = BeautifulSoup(response.text, 'lxml')
    except Exception as e:
        print(f'Error scraping CNN article.')
        return None
    
    if response.status_code != 200:
        return None

    # Parse into soup as lxml
    soup = BeautifulSoup(response.text, 'lxml')

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
    response = requests.get(url)

    # if no response return
    if response.status_code != 200:
        return None

    # Setup robots parser
    rp = read_robots_txt(url)
    crawl_delay = rp.crawl_delay('*')

    # Parse all text to lxml
    soup = BeautifulSoup(response.text, 'lxml')
    # Find all links to articles
    links_div = soup.find_all('div', class_=('container__field-links'))

    seen_urls = set()
    if links_div:
        for div in links_div:
            for link in div.find_all('a',href=True):
                href = link.get('href')
                if href.startswith('/'):
                    href = urljoin(url, href)

                # Improve runtime and make sure articles are not read twice and respect robots.txt
                if href in seen_urls or not rp.can_fetch('*', href):
                    continue
                seen_urls.add(href)

                # Wait between 3-15 seconds to look human
                time.sleep(crawl_delay if crawl_delay else random.randint(3,15))

                article = CNN(href)

                if article:
                    update_queue.put((text_widget, article.__str__()))

    return

def fox(url):
    # Exception handling, return nothing if Fox freezes
    try:
        response = requests.get(url, timeout=.5)
        soup = BeautifulSoup(response.text, 'lxml')
    except Exception as e:
        print(f'Error scraping fox article.')
        return None
    
    if response.status_code != 200:
        return None
    
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
    response = requests.get(url)
    https = 'https:'

    # If no response return
    if response.status_code != 200:
        return None
    
    rp = read_robots_txt(url)
    crawl_delay = rp.crawl_delay('*')

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
                if rp.can_fetch('*', href):
                    # Wait between 3-15 seconds to look human
                    time.sleep(crawl_delay if crawl_delay else random.randint(3, 15))

                    article = fox(href)

                    if article:
                        update_queue.put((text_widget, article.__str__()))

    return

# Define npr
def npr(url):
    # Exception handling, return nothing if Fox freezes
    try:
        response = requests.get(url, header, timeout=.5)
        soup = BeautifulSoup(response.text, 'lxml')
    except Exception as e:
        print(f'Error scraping fox article.')
        return None
    
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
    try:
        response = requests.get(url, header)
        # print(response.text)
    except Exception as e:
        print(f'Error: {e}')
        return None

    if response.status_code != 200:
        print(f'Error: {response.status_code}')
        return None
    
    rp = read_robots_txt(url)
    crawl_delay = rp.crawl_delay('*')

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
                if href not in seen_urls and rp.can_fetch('*', href):
                    seen_urls.add(href)

                    # Wait between 3-15 seconds to look like human activity
                    time.sleep(crawl_delay if crawl_delay else random.randint(3, 15))

                    article = npr(href)

                    if article:
                        update_queue.put((text_widget, article.__str__()))
                    
    return

def techcrunch_grabber(url, text_widget):
    try:
        response = requests.get(url, timeout=10)
    except Exception as e:
        print(f'Error: {e}')
        return None

def main():
    # Political News
    cnn_url = 'https://www.cnn.com'
    fox_url = 'https://www.foxnews.com'
    npr_url = 'https://www.npr.org'

    # Tech News
    techcrunch_url = 'https://techcrunch.com'

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
    threading.Thread(target=scrape_and_print, args=(CNN_grabber, cnn_url, text_widgets[0],)).start()
    threading.Thread(target=scrape_and_print, args=(fox_grabber, fox_url, text_widgets[0],)).start()
    threading.Thread(target=scrape_and_print, args=(npr_grabber, npr_url, text_widgets[0],)).start()

    window.after(15, update_gui, window)

    time.sleep(20)

    # Disable configuration so user cannot type in widget
    # for widget in text_widgets:
    #     widget.config(state='disable')

    # Initialize window
    window.mainloop()

main()