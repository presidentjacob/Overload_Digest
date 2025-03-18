import requests
import validators
import textwrap
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import tkinter.font as font
from tkinter import Label
from bs4 import BeautifulSoup

# Setup an article class to contain article information
class Article:
    def __init__(self):
        self.header = ''
        self.subheader = ''
        self.author = ''
        self.time = ''
        self.paragraphs = ''
    def __str__(self):
        return f'\n{self.header}\n{self.subheader}\n{self.author}\n{self.time}\n{self.paragraphs}'

# Create different user agents to look human
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
]

# Separator between articles
separator = '-' * 70

# Define auto_scroll
def auto_scroll(text_widget):
    # Set each to scroll at the exact same speed
    total_lines = int(text_widget.index('end-1c').split('.')[0])
    speed = .05 / total_lines
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

# Define CNN grabber
def CNN(url):
    try:
        response = requests.get(url, timeout=.5)
        soup = BeautifulSoup(response.text, 'lxml')
    except Exception as e:
        print(f'Error scraping article')
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
    cnn_article = Article()
    full_article = ''

    # Only add information to the article class only if paragraph_div exists
    # If there are no paragraphs, the article will not be added.
    if headline and paragraph_div:
        setattr(cnn_article, 'header', (headline.text.strip()))

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
def CNN_grabber(url):
    response = requests.get(url)

    # if no response return
    if response.status_code != 200:
        return None

    # Parse all text to lxml
    soup = BeautifulSoup(response.text, 'lxml')
    # Find all links to articles
    links_div = soup.find_all('div', class_=('container__field-links'))

    all_articles = []
    seen_urls = set()
    if links_div:
        for div in links_div:
            for link in div.find_all('a',href=True):
                href = link.get('href')
                # Improve runtime and make sure articles are not read twice
                if (href in seen_urls or any(exclude in href for exclude in ['/podcasts', '/fashion', '/deals', '/interactive', '/video', '/bleacherreport'])):
                    continue
                seen_urls.add(href)

                if href.startswith('/'):
                    href = url + href

                article = CNN(href)

                if article:
                    all_articles.append(article)

    return all_articles

def fox(url):
    # Exception handling, return nothing if Fox freezes
    try:
        response = requests.get(url, timeout=.5)
        soup = BeautifulSoup(response.text, 'lxml')
    except Exception as e:
        print(f'Error scraping article')
        return None
    
    if response.status_code != 200:
        return None
    # Parse into soup as lxml
    soup = BeautifulSoup(response.text, 'lxml')

    header_div = soup.find('div', class_='article-meta article-meta-upper')
    headline = header_div.find('h1') if header_div else None
    subheader = header_div.find('h2') if header_div else None
    author_div = soup.find('div', class_='author-byline')
    date_span = soup.find('span', class_='article-date')
    paragraph_p = soup.find_all('p')

    fox_article = Article()
    full_article = ''

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
def fox_grabber(url):
    response = requests.get(url)
    https = 'https:'

    # If no response return
    if response.status_code != 200:
        return None
    
    # Parse all html text as lxml
    soup = BeautifulSoup(response.text, 'lxml')

    # Find all links to articles
    all_links = soup.find_all('header', class_=('info-header'))
    

    all_articles = []
    # Setup seen headlines so headlines are not displayed twice.

    # If links exist
    if all_links:
        # For all found
        for links in all_links:
            # Find 'a' who's href is true
            for link in links.find_all('a', href=True):
                href = link.get('href')
                # Ignore anything that isn't news
                if (any(site in href for site in ['foxnews', 'foxbusiness', 'foxweather']) and not '/video' in href and not '/radio' in href):
                    if href.startswith('/'):
                        href = https + href

                    article = fox(href)

                    if article:
                        all_articles.append(article)

    return all_articles

# Define nytimes_grabber
def npr_grabber(url):
    # Use headers to make it look as if program is a user and not a bot
    header = {
        'User-Agent': f'{user_agents[0]}',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Referer': 'http://www.google.com/',
        'Upgrade-Insecure-Requests': '1',
    }

    try:
        response = requests.get(url, header)
        # print(response.text)
    except Exception as e:
        print(f'Error: {e}')
        return None

    # if response != '200':
    #     print(f'Error: {response.status_code}')
    #     return
    
    # Setup a readable text
    soup = BeautifulSoup(response.text, 'lxml')

    # Find all links to articles
    links_div = soup.find('div', class_='story-text')

    all_articles = []

    for link in links_div.find_all('a', href=True):
        href = link.get('href')
        print(href)

    return all_articles

def main():
    cnn_url = 'https://www.cnn.com'
    fox_url = 'https://www.foxnews.com'
    npr_url = 'https://www.npr.org'

    cnn_articles = CNN_grabber(cnn_url)
    fox_articles = fox_grabber(fox_url)
    npr_articles = npr_grabber(npr_url)

    

    # Create main window
    window = tk.Tk()
    window.title('Overload Digest')
    window.geometry('640x480')
    window.configure(background='black')
    window.state('zoomed')

    # Create title headline on Overload Digest
    T1 = tk.Text(window, bg='black', fg='white', insertbackground='white', cursor='arrow')
    T1.tag_configure('center', justify='center', font=('Times New Roman', 50))
    T1.insert('1.0', 'OVERLOAD DIGEST')
    T1.tag_add('center', '1.0', 'end')
    T1.config(state='disable')
    T1.pack(expand=True, fill='both')

    frame = tk.Frame(window, bg='black')
    frame.pack(fill='both', expand=True)

    # Define a scrollbar for user to scroll through information
    scrollbar = tk.Scrollbar(frame, orient='vertical')
    text_widgets = []

    # Setup text widgets for articles to be inserted.
    for i in range(3):
        text = tk.Text(frame, wrap='word', bg='black', fg='white', insertbackground='white', cursor='arrow',
                       yscrollcommand=scrollbar.set, font=('Times New Roman', 15))
        text.grid(row=0, column=i, sticky='nsew', padx = 10, pady=10)
        # text.config(state='enable')
        text_widgets.append(text)
        auto_scroll(text)

    # Configure column resizing
    for i in range(3):
        frame.columnconfigure(i, weight=1)
    frame.rowconfigure(0, weight=1)

    # Insert article content to text_widgets
    for article in cnn_articles[::-1]:
        text_widgets[0].insert('1.0', article.__str__())
    
    for article in fox_articles:
        text_widgets[1].insert('1.0', article.__str__())

    # Disable configuration so user cannot type in widget
    for widget in text_widgets:
        widget.config(state='disable')

    # Initialize window
    window.mainloop()

main()