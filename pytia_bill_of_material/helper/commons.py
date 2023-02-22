"""
    Submodule for common classes and functions.
"""

import re
from tkinter import DISABLED, NORMAL

from app.main.layout import Layout
from resources import resource


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
            self.layout.tree_report_failed_props.delete(
                *self.layout.tree_report_failed_props.get_children()
            )
            self.layout.text_description.configure(state=NORMAL)
            self.layout.text_description.delete("1.0", "end")
            self.layout.text_description.configure(state=DISABLED)

            self.layout.button_open_document.configure(state=DISABLED)
            self.layout.button_open_parent.configure(state=DISABLED)
            self.layout.button_close_document.configure(state=DISABLED)
            self.layout.tree_report_failed_items.state(("!disabled",))
        except IndexError:
            pass


class ResourceCommons:
    @staticmethod
    def get_property_names_from_config(header: list) -> tuple:
        """
        Returns a tuple containing the property names of the bom.json header items.
        Returns the header name if an item is not a property.
        """
        prop_names = ()
        for item in header:
            if ":" in item:
                prop_names += (item.split(":")[-1],)
            elif "=" in item:
                prop_names += (item.split("=")[0],)
            else:
                prop_names += (item,)
        return prop_names

    @staticmethod
    def get_header_names_from_config(header: list) -> tuple:
        """
        Returns a tuple containing the header names of the bom.json header items.
        """
        return tuple([s for s in re.split("[:|=]+", i)][0] for i in header)
