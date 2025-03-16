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
        self.header = ""
        self.subheader = ""
        self.author = ""
        self.time = ""
        self.paragraphs = ""
    def __str__(self):
        return f"\n{self.header}\n{self.subheader}\n{self.author}\n{self.time}\n{self.paragraphs}"

# Separator between articles
separator = '-' * 70

# Define auto_scroll
def auto_scroll(text_widget):
    # Set speed low, 0.000005 seems to work best for nice speed
    speed = 0.000005
    current_position = text_widget.yview()[0]

    # Reset position to the top if the autoscroll reaches the bottom.
    if current_position < 1:
        text_widget.yview_moveto(current_position + speed)
        text_widget.after(50, lambda: auto_scroll(text_widget))
    else:
        text_widget.yview_moveto(0.0)
        text_widget.after(50, lambda: auto_scroll(text_widget))

def print_paragraph(text):
    line_length = 70
    wrapped_text = textwrap.fill(text, line_length)
    return wrapped_text

# Define CNN grabber
def CNN(url):
    response = requests.get(url)

    # Parse into soup as lxml
    soup = BeautifulSoup(response.text, 'lxml')

    # Get all information regarding file
    header_div = soup.find("div", class_="headline__wrapper")
    headline = header_div.find("h1") if header_div else None
    subheader = header_div.find("h2") if header_div else None
    author_div = soup.find("div", class_="byline__names vossi-byline__names")
    time_div = soup.find("div", class_="timestamp vossi-timestamp")
    paragraph_div = soup.find("div", class_="article__content")

    # Create a new article
    cnn_article = Article()
    full_article = ""

    # Only add information to the article class only if paragraph_div exists
    # If there are no paragraphs, the article will not be added.
    if headline and paragraph_div:
        setattr(cnn_article, "header", (headline.text.strip()))

    if subheader and paragraph_div:
        setattr(cnn_article, "subheader", subheader.text.strip() + '\n')

    if author_div and paragraph_div:
        authors = [authors.text.strip() for authors in soup.find_all("span", class_="byline__name")]
        setattr(cnn_article, "author", ", ".join(authors) + '\n')

    if time_div and paragraph_div:
        time = time_div.text
        time = time.replace("Updated", "")
        time = time.replace("Published", "")
        setattr(cnn_article, "time", time.strip() + '\n')

    if paragraph_div:
        for paragraph in paragraph_div.find_all("p"):
            full_article += print_paragraph(paragraph.text.strip()) +"\n\n"
        full_article += separator
        setattr(cnn_article, "paragraphs", full_article)

    return cnn_article

# Define a grabber for CNN.com
def CNN_grabber(url):
    response = requests.get(url)

    # if no response return
    if response.status_code != 200:
        return

    # Parse all text to lxml
    soup = BeautifulSoup(response.text, 'lxml')
    # Find all links to articles
    links_div = soup.find_all("div", class_=("container__field-links", "container_title"))

    all_articles = []
    seen_headlines = set()
    if links_div:
        for div in links_div:
            for link in div.find_all("a",href=True):
                href = link.get('href')

                if href.startswith("/"):
                    href = url + href

                article = CNN(href)
                if article and article.header not in seen_headlines:
                    all_articles.append(article)
                    seen_headlines.add(article.header)

    return all_articles

def fox_grabber(url):
    response = requests.get(url)

    # If no response return
    if response.status_code != 200:
        return

def main():
    cnn_url = "https://www.cnn.com"
    fox_url = "https://www.foxnews.com"
    cnn_articles = CNN_grabber(cnn_url)
    fox_articles = fox_grabber(fox_url)

    # Create main window
    window = tk.Tk()
    window.title("Overload Digest")
    window.geometry('1000x1000')
    window.configure(background="black")

    # Create title headline on Overload Digest
    T1 = tk.Text(window, bg="black", fg="white", insertbackground="white", cursor="arrow")
    T1.tag_configure("center", justify='center', font=("Times New Roman", 50))
    T1.insert("1.0", "OVERLOAD DIGEST")
    T1.tag_add("center", "1.0", "end")
    T1.config(state="disable")
    T1.pack(expand=True, fill="both")

    frame = tk.Frame(window, bg="black")
    frame.pack(fill="both", expand=True)

    # Define a scrollbar for user to scroll through information
    scrollbar = tk.Scrollbar(frame, orient="vertical")
    text_widgets = []

    # Setup text widgets for articles to be inserted.
    for i in range(3):
        text = tk.Text(frame, wrap="word", bg="black", fg="white", insertbackground="white", cursor="arrow",
                       yscrollcommand=scrollbar.set, font=("Times New Roman", 15))
        text.grid(row=0, column=i, sticky="nsew", padx = 10, pady=10)
        # text.config(state="enable")
        text_widgets.append(text)
        auto_scroll(text)

    # Configure column resizing
    for i in range(3):
        frame.columnconfigure(i, weight=1)
    frame.rowconfigure(0, weight=1)

    # Insert article content to text_widgets
    for article in cnn_articles[::-1]:
        text_widgets[0].insert("1.0", article.__str__())

    # Disable configuration so user cannot type in widget
    for widget in text_widgets:
        widget.config(state="disable")

    # Initialize window
    window.mainloop()

main()