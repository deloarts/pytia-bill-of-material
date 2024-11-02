"""
    Submodule for common classes and functions.
"""

import re
from tkinter import DISABLED
from tkinter import NORMAL

from app.main.layout import Layout


class CallbackCommons:
    """Commons class for the callback class."""

    def __init__(self, layout: Layout) -> None:
        """
        Inits the Commons class. Requires the layout of the main window.

        Args:
            layout (Layout): The layout of the main window.
        """
        self.layout = layout

    def remove_selection_from_failed_items(self) -> None:
        """Removes the selection from the failed items widget."""
        try:
            selection = self.layout.tree_report_failed_items.selection()[0]
            self.layout.tree_report_failed_items.delete(selection)
            self.layout.tree_report_failed_props.delete(*self.layout.tree_report_failed_props.get_children())
            self.layout.text_description.configure(state=NORMAL)
            self.layout.text_description.delete("1.0", "end")
            self.layout.text_description.configure(state=DISABLED)

            self.layout.button_open_document.configure(state=DISABLED)
            self.layout.button_open_parent.configure(state=DISABLED)
            self.layout.button_close_document.configure(state=DISABLED)
            self.layout.tree_report_failed_items.state(("!disabled",))
        except IndexError:
            pass
