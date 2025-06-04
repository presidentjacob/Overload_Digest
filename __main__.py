import threading, logging
from scraper.abc import abc_grabber
from scraper.bbc import bbc_grabber
from scraper.cbs import cbs_grabber
from scraper.fox import fox_grabber
from scraper.npr import npr_grabber
from scraper.techcrunch import techcrunch_grabber
from scraper.fourmedia import four_media_grabber
from scraper.wired import wired_grabber
from scraper.cnn import cnn_grabber
from gui import update_gui, create_loading_window, create_main_window
import time
import queue
from utils import scrape_and_print

logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info('Starting Overload Digest')
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

    update_queue = queue.Queue()

    loading_window = create_loading_window()
    window, text_widgets = create_main_window()

    # CNN_grabber(cnn_url, text_widgets[0])
    # fox_grabber(fox_url, text_widgets[1])
    # npr_grabber(npr_url, text_widgets[2])

    # Run threads to update per each article scraped.
    logging.info('Starting threads')
    threading.Thread(target=scrape_and_print, args=(cnn_grabber, cnn_url, text_widgets[0], update_queue)).start()
    threading.Thread(target=scrape_and_print, args=(fox_grabber, fox_url, text_widgets[0], update_queue)).start()
    threading.Thread(target=scrape_and_print, args=(npr_grabber, npr_url, text_widgets[0], update_queue)).start()

    threading.Thread(target=scrape_and_print, args=(techcrunch_grabber, techcrunch_url, text_widgets[1], update_queue)).start()
    threading.Thread(target=scrape_and_print, args=(four_media_grabber, four_zero_four_media_url, text_widgets[1], update_queue)).start()
    threading.Thread(target=scrape_and_print, args=(wired_grabber, wired_url, text_widgets[1], update_queue)).start()

    threading.Thread(target=scrape_and_print, args=(bbc_grabber, bbc_url, text_widgets[2], update_queue)).start()
    threading.Thread(target=scrape_and_print, args=(cbs_grabber, cbs_url, text_widgets[2], update_queue)).start()
    threading.Thread(target=scrape_and_print, args=(abc_grabber, abc_url, text_widgets[2], update_queue)).start()

    window.after(15, update_gui, window, update_queue)

    time.sleep(40)
    # Disable configuration so user cannot type in widget
    # for widget in text_widgets:
    #     widget.config(state='disable')
    loading_window.destroy()
    window.deiconify()

    # Initialize window
    window.mainloop()

main()