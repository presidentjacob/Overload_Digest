import urllib.robotparser
import logging
from urllib.parse import urljoin

# Function for threading
def scrape_and_print(function, url, widget):
        logging.info(f'Starting scrape for {url} using {function.__name__}')
        function(url, widget)

# Function to read robots.txt file
def read_robots_txt(url):
    logging.info(f'Reading robots.txt for {url}')
    rp = urllib.robotparser.RobotFileParser()
    robots_url = urljoin(url, '/robots.txt')
    try:
        # Read robots.txt and return rp
        rp.set_url(robots_url)
        rp.read()
        return rp
    except Exception as e:
        logging.error(f'Error reading robots.txt: {e}')
        return None