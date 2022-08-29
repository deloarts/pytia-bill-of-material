"""
    Helper functions for messages.
"""

import webbrowser
from tkinter import messagebox as tkmsg

from resources import resource


def show_help() -> None:
    """Opens the help docs."""
    if url := resource.settings.urls.help:
        webbrowser.open_new(url)
    else:
        tkmsg.showinfo(
            title=resource.settings.title,
            message="Your administrator did not provide a help page for this app.",
        )
