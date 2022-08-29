"""
    Submodule for managing the state of the widgets.
    Two states are available:

    - Normal
    - Disabled
"""

import os
import tkinter as tk
from pathlib import Path

from app.main.layout import Layout
from app.main.vars import Variables
from helper.lazy_loaders import LazyDocumentHelper
from pytia_ui_tools.handlers.workspace_handler import Workspace
from resources import resource
from templates import templates


class UISetter:
    """UI Setter class for the main window."""

    def __init__(
        self,
        root: tk.Tk,
        layout: Layout,
        variables: Variables,
        lazy_document_helper: LazyDocumentHelper,
        workspace: Workspace,
    ) -> None:
        """Inits the UI Setter class for the main window.

        Args:
            root (tk.Tk): The main window object.
            layout (Layout): The layout of the main window.
            variables (Variables): The variables of the main window.
            lazy_document_helper (LazyDocumentHelper): The lazy document helper instance.
            workspace (Workspace): The workspace instance.
        """
        self.root = root
        self.layout = layout
        self.doc_helper = lazy_document_helper
        self.vars = variables
        self.workspace = workspace

        self._state_checkbox_export_docket = tk.NORMAL
        self._state_checkbox_export_stp = tk.NORMAL
        self._state_checkbox_export_stl = tk.NORMAL

    def normal(self) -> None:
        """
        Sets the UI to state 'Normal'. Sets the cursor to 'arrow'.
        """
        self.layout.input_project.configure(
            state="readonly"
            if resource.settings.restrictions.strict_project
            and self.workspace.elements.projects
            else tk.NORMAL
        )

        self.layout.input_bom_export_path.configure(state=tk.NORMAL)
        self.layout.button_bom_export_path.configure(state=tk.NORMAL)

        self.layout.input_docket_export_path.configure(
            state=tk.NORMAL if templates.docket_path is not None else tk.DISABLED
        )
        self.layout.button_docket_export_path.configure(
            state=tk.NORMAL if templates.docket_path is not None else tk.DISABLED
        )

        self.layout.input_stp_export_path.configure(state=tk.NORMAL)
        self.layout.button_stp_export_path.configure(state=tk.NORMAL)

        self.layout.input_stl_export_path.configure(state=tk.NORMAL)
        self.layout.button_stl_export_path.configure(state=tk.NORMAL)

        self.layout.checkbox_export_docket.configure(
            state=self._state_checkbox_export_docket
            if os.path.isdir(self.vars.docket_export_path.get())
            and templates.docket_path is not None
            else tk.DISABLED
        )
        self.layout.checkbox_export_stp.configure(
            state=self._state_checkbox_export_stp
            if os.path.isdir(self.vars.stp_export_path.get())
            else tk.DISABLED
        )
        self.layout.checkbox_export_stl.configure(
            state=self._state_checkbox_export_stl
            if os.path.isdir(self.vars.stl_export_path.get())
            else tk.DISABLED
        )

        self.layout.button_export.configure(
            state=tk.NORMAL
            if os.path.isdir(Path(self.vars.bom_export_path.get()).parent)
            and ".xlsx" in self.vars.bom_export_path.get()
            else tk.DISABLED
        )
        self.layout.button_exit.configure(state=tk.NORMAL)

        self.root.config(cursor="arrow")

    def disabled(self) -> None:
        """
        Sets the UI to state 'Disabled'. Exit button will stay available.
        Sets the cursor to 'arrow'.
        """
        self.layout.input_project.configure(state=tk.DISABLED)

        self.layout.input_bom_export_path.configure(state=tk.DISABLED)
        self.layout.button_bom_export_path.configure(state=tk.DISABLED)

        self.layout.input_docket_export_path.configure(state=tk.DISABLED)
        self.layout.button_docket_export_path.configure(state=tk.DISABLED)

        self.layout.input_stp_export_path.configure(state=tk.DISABLED)
        self.layout.button_stp_export_path.configure(state=tk.DISABLED)

        self.layout.input_stl_export_path.configure(state=tk.DISABLED)
        self.layout.button_stl_export_path.configure(state=tk.DISABLED)

        self._state_checkbox_export_docket = self.layout.checkbox_export_docket.state()
        self.layout.checkbox_export_docket.configure(state=tk.DISABLED)

        self._state_checkbox_export_stp = self.layout.checkbox_export_stp.state()
        self.layout.checkbox_export_stp.configure(state=tk.DISABLED)

        self._state_checkbox_export_stl = self.layout.checkbox_export_stl.state()
        self.layout.checkbox_export_stl.configure(state=tk.DISABLED)

        self.layout.button_export.configure(state=tk.DISABLED)

        self.root.config(cursor="arrow")

    def working(self) -> None:
        """
        Sets the UI to state 'Working'. Sets the cursor to 'wait'.
        """
        self.disabled()
        self.root.config(cursor="wait")
        self.layout.button_exit.configure(state=tk.DISABLED)
