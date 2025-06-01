# Overload_Digest
A Python-based GUI application that scrapes 9 news sources and auto-scrolls front articles using `requests`, `BeautifulSoup`, `Selenium`, and `Tkinter`

## Features
* Scrapes political and tech articles from CNN, Fox, NPR, TechCrunch, and more.
* Uses BeautifulSoup to scrape from websites` home pages and articles and parse content.
* Uses `Selenium` and `BeautifulSoup` to bypass dynamically loaded content.
* Applies and auto-scrolling feature to simulate a newsfeed GUI.
* Incorporates threading to prevent GUI freezing and increase run speed while also adding articles to the GUI as they`re scraped.
* Respects `robots.txt` for ethical scraping.
* Includes user-agent headers to mimic human browsing.
![image](https://github.com/user-attachments/assets/600edf37-5c24-4096-9bc7-3820531b5290)

## Installation
### Prerequisites
* Python 3.8+
* Google Chrome and ChromeDriver are installed.
### Install Required Packages
Run this command in your bash terminal:
`pip install requests beautifulsoup4 lxml selenium`

## Running the program
Enter this prompt into your bash terminal:
`python overloaddigest.py`

## Sources Implemented
* CNN
* Fox News
* NPR
* TechCrunch
* Wired
* 4040 Media
* BBC
* CBS News
* ABC News

## How overloaddigest works
1. **Open URL**: If the webpage has dynamically loaded content, it uses `Selenium` to retrieve content; otherwise, it will check the response code from `requests`.
2. **Parse HTML**: `BeautifulSoup` is then used to extract homepage elements in `lxml` format.
3. **Respect Bots**: The program will check `robots.txt` and apply crawl delays if applicable, and check allowed articles to scrape.
4. **Scraping Articles**: If the article is dynamically loaded, `Selenium` is used to extract content, else `requests` is used. `BeautifulSoup` then extracts all elements in `lxml` format.
5. **Display**: Article information is placed in a `queue` and rendered in the `ScrolledText` widgets.
6. **Threading**: Background scraping runs in threads to dynamically update the GUI over time and improve performance and run speed.
7. **Auto-Scroll**: Simulates a continuous scrolling news feed effect.

## Development Notes
* GUI is created with `tkinter`, using `Label` widgets for headlines and `ScrolledText` for the article body.
* Modular scraping functions (`*_grabber`) allow for easy addition of new news sources.
* Each article is in an `Article` class for consistent formatting.
* Code style emphasizes readability and modularity.

## To Do / Known Issues
* Take information on a user's computer to format separators better.
* Date time is formatted wrong in some articles like Wired.
* Improve/standardized formatting.
* Wired's formatting for authors is broken.