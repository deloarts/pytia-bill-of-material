"""
    The GUI for the application.
"""

import tkinter as tk
from pathlib import Path
from tkinter import font, ttk

from const import APP_VERSION, LOG, LOGS
from helper.lazy_loaders import LazyDocumentHelper
from helper.messages import show_help
from pytia.exceptions import (
    PytiaBodyEmptyError,
    PytiaDifferentDocumentError,
    PytiaDocumentNotSavedError,
    PytiaNoDocumentOpenError,
    PytiaPropertyNotFoundError,
    PytiaWrongDocumentTypeError,
)
from pytia_ui_tools.exceptions import PytiaUiToolsOutsideWorkspaceError
from pytia_ui_tools.handlers.error_handler import ErrorHandler
from pytia_ui_tools.handlers.mail_handler import MailHandler
from pytia_ui_tools.handlers.workspace_handler import Workspace
from pytia_ui_tools.window_manager import WindowManager
from resources import resource

from app.main.callbacks import Callbacks
from app.main.controller import Controller
from app.main.frames import Frames
from app.main.layout import Layout
from app.main.tooltips import ToolTips
from app.main.traces import Traces
from app.main.ui_setter import UISetter
from app.main.vars import Variables


class MainUI(tk.Tk):
    """The user interface of the app."""

    WIDTH = 600
    HEIGHT = 410

    def __init__(self) -> None:
        tk.Tk.__init__(self)

        # CLASS VARS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.doc_helper: LazyDocumentHelper  # Instantiate later for performance improvement
        self.workspace: Workspace  # Instantiate later, dependent on doc_helper
        self.set_ui: UISetter  # Instantiate later, dependent on doc_helper
        self.vars = Variables(root=self)
        self.frames = Frames(root=self)
        self.layout = Layout(
            root=self,
            frames=self.frames,
            variables=self.vars,
        )

        # UI TOOLS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.window_manager = WindowManager(self)
        self.mail_handler = MailHandler(
            standard_receiver=resource.settings.mails.admin,
            app_title=resource.settings.title,
            app_version=APP_VERSION,
            logfile=Path(LOGS, LOG),
        )
        self.error_handler = ErrorHandler(
            mail_handler=self.mail_handler,
            warning_exceptions=[
                PytiaNoDocumentOpenError,
                PytiaWrongDocumentTypeError,
                PytiaBodyEmptyError,
                PytiaPropertyNotFoundError,
                PytiaDifferentDocumentError,
                PytiaDocumentNotSavedError,
                PytiaUiToolsOutsideWorkspaceError,
            ],
        )

        # UI INIT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.title(
            f"{resource.settings.title} "
            f"{'(DEBUG MODE)' if resource.settings.debug else APP_VERSION}"
        )
        self.attributes("-topmost", True)
        self.attributes("-toolwindow", True)
        self.config(cursor="wait")
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="Segoe UI", size=9)
        self.report_callback_exception = self.error_handler.exceptions_callback

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (MainUI.WIDTH / 2))
        y_coordinate = int((screen_height / 2) - (MainUI.HEIGHT / 2) - 20)
        self.geometry(f"{MainUI.WIDTH}x{MainUI.HEIGHT}+{x_coordinate}+{y_coordinate}")
        self.minsize(width=MainUI.WIDTH, height=MainUI.HEIGHT)
        self.resizable(width=False, height=False)

        # STYLES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        style = ttk.Style(self)
        style.configure("Infrastructure.TLabelframe.Label", foreground="grey")
        style.configure("Paths.TLabelframe.Label", foreground="grey")
        style.configure("Export.TLabelframe.Label", foreground="grey")
        style.configure("Report.TLabelframe.Label", foreground="grey")
        style.configure("Footer.TButton", width=14)

        self.update()
        self.window_manager.remove_window_buttons()

    def run(self) -> None:
        """Run the app."""
        self.after(100, self._run)
        self.mainloop()

    def _run(self) -> None:
        """Runs all controllers. Initializes all lazy loaders."""

        # Setup doc helper
        self.doc_helper = LazyDocumentHelper()
        self.vars.initial_filepath = self.doc_helper.path

        # Setup the workspace
        self.workspace = Workspace(
            path=self.doc_helper.path,
            filename=resource.settings.files.workspace,
            allow_outside_workspace=resource.settings.restrictions.allow_outside_workspace,
        )
        self.workspace.read_yaml()
        if ws_title := self.workspace.elements.title:
            self.title(f"{self.title()}  -  {ws_title} (Workspace)")

        # Setup the ui state handler
        self.set_ui = UISetter(
            root=self,
            layout=self.layout,
            variables=self.vars,
            lazy_document_helper=self.doc_helper,
            workspace=self.workspace,
        )

        # Setup the controller
        controller = Controller(
            root=self,
            doc_helper=self.doc_helper,
            layout=self.layout,
            vars=self.vars,
            ui_setter=self.set_ui,
            workspace=self.workspace,
        )
        controller.run_all_controllers()

        # Setup callbacks, traces and bindings
        self.callbacks()
        self.traces()
        self.bindings()
        self.tooltips()

    def bindings(self) -> None:
        """Key bindings."""
        self.bind("<Escape>", lambda _: self.destroy())
        self.bind("<F1>", lambda _: show_help())

    def callbacks(self) -> None:
        """Instantiates the Callbacks class."""
        Callbacks(
            root=self,
            variables=self.vars,
            lazy_document_helper=self.doc_helper,
            layout=self.layout,
            workspace=self.workspace,
            ui_setter=self.set_ui,
        )

    def traces(self) -> None:
        """Instantiates the traces class."""
        Traces(
            root=self,
            variables=self.vars,
            state_setter=self.set_ui,
            frames=self.frames,
            layout=self.layout,
            workspace=self.workspace,
        )

    def tooltips(self) -> None:
        """Instantiates the tooltips class."""
        ToolTips(layout=self.layout, workspace=self.workspace)
