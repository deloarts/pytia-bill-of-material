"""
    Submodule for managing the state of the widgets.
    Two states are available:

    - Normal
    - Disabled
"""

import os
import re
import tkinter as tk
from pathlib import Path

from app.main.frames import Frames
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
        frames: Frames,
        lazy_document_helper: LazyDocumentHelper,
        workspace: Workspace,
    ) -> None:
        """Inits the UI Setter class for the main window.

        Args:
            root (tk.Tk): The main window object.
            layout (Layout): The layout of the main window.
            variables (Variables): The variables of the main window.
            frames (Frames): The frames of the main.
            lazy_document_helper (LazyDocumentHelper): The lazy document helper instance.
            workspace (Workspace): The workspace instance.
        """
        self.root = root
        self.layout = layout
        self.doc_helper = lazy_document_helper
        self.vars = variables
        self.frames = frames
        self.workspace = workspace

        self._state_checkbox_export_docket = tk.NORMAL
        self._state_checkbox_export_drawing = tk.NORMAL
        self._state_checkbox_export_stp = tk.NORMAL
        self._state_checkbox_export_stl = tk.NORMAL
        self._state_checkbox_export_jpg = tk.NORMAL

        self._state_checkbox_ignore_prefixed = tk.NORMAL
        self._state_checkbox_ignore_unknown = tk.NORMAL

    def normal(self) -> None:
        """
        Sets the UI to state 'Normal'. Sets the cursor to 'arrow'.
        """

        self.layout.progress_bar.grid_remove()
        self.frames.log.grid_remove()

        if not self.vars.show_report.get():
            self.frames.infrastructure.grid()
            self.frames.paths.grid()
            self.frames.export.grid()

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

        self.layout.input_drawing_export_path.configure(state=tk.NORMAL)
        self.layout.button_drawing_export_path.configure(state=tk.NORMAL)

        self.layout.input_stp_export_path.configure(state=tk.NORMAL)
        self.layout.button_stp_export_path.configure(state=tk.NORMAL)

        self.layout.input_stl_export_path.configure(state=tk.NORMAL)
        self.layout.button_stl_export_path.configure(state=tk.NORMAL)

        self.layout.input_jpg_export_path.configure(state=tk.NORMAL)
        self.layout.button_jpg_export_path.configure(state=tk.NORMAL)

        self.layout.checkbox_export_docket.configure(
            state=self._state_checkbox_export_docket
            if os.path.isdir(self.vars.docket_export_path.get())
            and templates.docket_path is not None
            else tk.DISABLED
        )
        self.layout.checkbox_export_drawing.configure(
            state=self._state_checkbox_export_drawing
            if os.path.isdir(self.vars.drawing_export_path.get())
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
        self.layout.checkbox_export_jpg.configure(
            state=self._state_checkbox_export_jpg
            if os.path.isdir(self.vars.jpg_export_path.get())
            else tk.DISABLED
        )
        self.layout.checkbox_ignore_source_unknown.configure(
            state=self._state_checkbox_ignore_unknown
        )
        self.layout.checkbox_ignore_prefixed.configure(
            state=self._state_checkbox_ignore_prefixed
            if len(self.vars.ignore_prefix_txt.get()) > 0
            else tk.DISABLED
        )
        self.layout.input_ignore_prefixed_txt.configure(state=tk.NORMAL)

        self.set_button_export()
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

        self.layout.input_drawing_export_path.configure(state=tk.DISABLED)
        self.layout.button_drawing_export_path.configure(state=tk.DISABLED)

        self.layout.input_stp_export_path.configure(state=tk.DISABLED)
        self.layout.button_stp_export_path.configure(state=tk.DISABLED)

        self.layout.input_stl_export_path.configure(state=tk.DISABLED)
        self.layout.button_stl_export_path.configure(state=tk.DISABLED)

        self.layout.input_jpg_export_path.configure(state=tk.DISABLED)
        self.layout.button_jpg_export_path.configure(state=tk.DISABLED)

        self._state_checkbox_export_docket = self.layout.checkbox_export_docket.state()
        self.layout.checkbox_export_docket.configure(state=tk.DISABLED)

        self._state_checkbox_export_drawing = (
            self.layout.checkbox_export_drawing.state()
        )
        self.layout.checkbox_export_drawing.configure(state=tk.DISABLED)

        self._state_checkbox_export_stp = self.layout.checkbox_export_stp.state()
        self.layout.checkbox_export_stp.configure(state=tk.DISABLED)

        self._state_checkbox_export_stl = self.layout.checkbox_export_stl.state()
        self.layout.checkbox_export_stl.configure(state=tk.DISABLED)

        self._state_checkbox_export_jpg = self.layout.checkbox_export_jpg.state()
        self.layout.checkbox_export_jpg.configure(state=tk.DISABLED)

        self._state_checkbox_ignore_unknown = (
            self.layout.checkbox_ignore_source_unknown.state()
        )
        self.layout.checkbox_ignore_source_unknown.configure(state=tk.DISABLED)

        self._state_checkbox_ignore_prefixed = (
            self.layout.checkbox_ignore_prefixed.state()
        )
        self.layout.checkbox_ignore_prefixed.configure(state=tk.DISABLED)
        self.layout.input_ignore_prefixed_txt.configure(state=tk.DISABLED)

        self.layout.button_export.configure(state=tk.DISABLED)

        self.root.config(cursor="arrow")

    def working(self) -> None:
        """
        Sets the UI to state 'Working'. Sets the cursor to 'wait'.
        """
        self.disabled()

        self.frames.infrastructure.grid_remove()
        self.frames.paths.grid_remove()
        self.frames.export.grid_remove()
        self.layout.progress_bar.grid()
        self.frames.log.grid()

        self.root.config(cursor="wait")
        self.layout.button_exit.configure(state=tk.DISABLED)
        self.root.update_idletasks()

    def set_button_export(self) -> None:
        """
        Sets the state of the 'Export button' depending on a set of rules.
        """
        if (
            os.path.isdir(Path(self.vars.bom_export_path.get()).parent)
            and ".xlsx" in self.vars.bom_export_path.get()
            and self.vars.project.get()
            and not re.match(r"^\s+$", self.vars.project.get())
        ):
            self.layout.button_export.configure(state=tk.NORMAL)
        else:
            self.layout.button_export.configure(state=tk.DISABLED)
