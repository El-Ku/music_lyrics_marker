import sys
import logging
from datetime import datetime

class StreamToWindow:
    def __init__(self, window, key):
        self.window = window
        self.key = key

    def write(self, message):
        if message.strip():  # Avoid empty message
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            formatted_message = f"{timestamp} - {message}\n"
            self.window.write_event_value(self.key, formatted_message)

    def flush(self):
        pass  # Flush method for compatibility

class SGHandler(logging.Handler):
    def __init__(self, window, key):
        logging.Handler.__init__(self)
        self.window = window
        self.key = key

    def emit(self, record):
        msg = self.format(record)
        self.window.write_event_value(self.key, msg)

def setup_logger(window, key):
    logger = logging.getLogger('LogWindow')
    logger.setLevel(logging.INFO)
    handler = SGHandler(window, key)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    sys.stdout = StreamToWindow(window, key)
