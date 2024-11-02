"""
    Submodule for document helper.
"""

import os
from pathlib import Path
from tkinter import DISABLED
from tkinter import NORMAL
from tkinter import Tk
from tkinter import messagebox as tkmsg

from app.main.layout import Layout
from helper.callbacks import CallbackCommons
from pycatia.in_interfaces.document import Document
from pytia.framework import framework
from resources import resource


class ReportDocument:
    """ReportDocument class. Handles documents for the bom report."""

    def __init__(self, root: Tk, commons: CallbackCommons, layout: Layout) -> None:
        """
        Inits the class.

        Args:
            root (Tk): The root windows.
            commons (CallbackCommons): Callback commons required by this class.
            layout (Layout): The layout of the main app.
        """
        self.path: Path | None = None
        self.root = root
        self.commons = commons
        self.layout = layout

    def close(self) -> None:
        """Closes the document."""
        document = Document(framework.catia.active_document.com_object)
        document.save()
        document.close()
        self.commons.remove_selection_from_failed_items()
        self.path = None

    def open_wait_for_close(self, path: Path) -> None:
        """Opens the document and waits unit it's closed by the user."""
        if path and os.path.isfile(path):
            self.path = path
            framework.catia.documents.open(self.path)
            self.layout.button_open_document.configure(state=DISABLED)
            self.layout.button_open_parent.configure(state=DISABLED)
            self.layout.button_close_document.configure(state=NORMAL)
            self.layout.tree_report_failed_items.state(
                (DISABLED,)
            )  # FIXME: This doesn't really
            # disable the widget. Somehow
            # the user can still select
            # other items. This results
            # in false behaviour for the
            # open doc button.
            self._wait_for_close()
        else:
            tkmsg.showerror(
                title=resource.settings.title,
                message=(f"Cannot open document {path!r}."),
            )

    def _wait_for_close(self) -> None:
        """Waits for the user to close the document."""
        if self.path is not None:
            path = Path(Document(framework.catia.active_document.com_object).full_name)
            if str(path) != str(self.path):
                self.commons.remove_selection_from_failed_items()
                self.path = None
            else:
                self.root.after(500, self._wait_for_close)
