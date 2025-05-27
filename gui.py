import queue, logging

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