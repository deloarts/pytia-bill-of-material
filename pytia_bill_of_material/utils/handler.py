"""
    Handler submodule.
"""

import atexit
import logging
from tkinter import END, Text, Tk

from pytia.log import log


class WidgetLogHandler(logging.Handler):
    """
    Handles logging to Text widgets. Highlights log levels.

    Example:
    ```
        log_format = logging.Formatter(f"%(asctime)s  %(levelname)s  %(message)s")
        widget_handler = WidgetLogHandler(self, self.layout.text_log)
        widget_handler.setLevel(logging.INFO)
        widget_handler.setFormatter(log_format)
        logger.addHandler(widget_handler)
    ```
    """

    def __init__(self, root: Tk, widget: Text):
        """
        Inits the WidgetLogHandler.

        Args:
            root (Tk): The root tkinter window.
            widget (Text): The widget to which the handler is attached.
        """
        logging.Handler.__init__(self)

        self._root = root
        self._widget = widget

        self._widget.tag_config("DATE", foreground="grey")
        self._widget.tag_config("TIME", foreground="grey")
        self._widget.tag_config("DEBUG", foreground="blue")
        self._widget.tag_config("INFO", foreground="green")
        self._widget.tag_config("WARNING", foreground="orange")
        self._widget.tag_config("ERROR", foreground="red")
        self._widget.tag_config("EXCEPTION", foreground="black", background="red")

        atexit.register(lambda: log.logger.removeHandler(self))

    def emit(self, record) -> None:
        """
        Prints a new log record to the widget.
        """
        msg = self.format(record).replace("\n", " ")
        self._widget.configure(state="normal")
        self._widget.insert(END, msg + "\n")
        self._widget.configure(state="disabled")
        self._widget.yview(END)

        self.search(keyword=r"(\d{4}-\d{2}-\d{2})", tag="DATE", regex=True)
        self.search("DEBUG")
        self.search("INFO")
        self.search("WARNING")
        self.search("ERROR")
        self.search("EXCEPTION")

        self._root.update_idletasks()

    def search(self, keyword: str, tag: str | None = None, regex: bool = False) -> None:
        """
        Search for keywords and highlight them in the widget.

        Args:
            keyword (str): The keyword to search for.
            tag (str | None, optional): The widget tag to use. If None the keyword will be used \
                as tag. Defaults to None.
            regex (bool): Whether to match the keyword using regular expressions or not. Defaults \
                to False.
        """
        if tag is None:
            tag = keyword

        pos = "1.0"
        while True:
            idx = self._widget.search(keyword, pos, END, regexp=regex)
            if not idx:
                break
            pos = f"{idx}+{len(keyword)}c"
            self._widget.tag_add(tag, idx, pos)
