import tkinter as tk
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
from gui import update_gui, auto_scroll
import time
import queue

logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_and_print(scraper_function, url, text_widget, update_queue):
    scraper_function(url, text_widget, update_queue)

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

    # Loading Screen
    loading_window = tk.Tk()
    loading_window.title('Loading...')
    loading_window.geometry('300x100')
    loading_window.configure(background='black')
    loading_label = tk.Label(loading_window, text='Loading Overload Digest...', bg='black', fg='white', font=('Fixedsys', 16))
    loading_label.pack(expand=True)
    loading_window.update()

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