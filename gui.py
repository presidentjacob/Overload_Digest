import queue, logging, time
import tkinter as tk

# Update the gui, and recursively update
def update_gui(window, update_queue):
    try:
        while True:
            # Take the queue content and insert in the widget
            widget, text = update_queue.get_nowait()
            widget.config(state='normal')
            widget.insert('end', text)
            widget.config(state='disable')
    except queue.Empty:
        logging.debug('Queue is empty, continuing')
        pass

    window.after(10, update_gui, window, update_queue)

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

def create_loading_window():
    # Loading Screen
    loading_window = tk.Tk()
    loading_window.title('Loading...')
    loading_window.geometry('300x100')
    loading_window.configure(background='black')
    loading_label = tk.Label(loading_window, text='Loading Overload Digest...', bg='black', fg='white', font=('Fixedsys', 16))
    loading_label.pack(expand=True)
    loading_window.update()
    return loading_window

def create_main_window():
    # Create main window
    window = tk.Tk()
    window.title('Overload Digest')
    window.geometry('1920x1080') 
    window.configure(background='black')
    window.state('zoomed')

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

    return window, text_widgets