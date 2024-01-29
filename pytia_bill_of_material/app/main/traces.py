"""
    Traces submodule for the app.
"""

import os
from pathlib import Path
from pathlib import WindowsPath
from tkinter import DISABLED
from tkinter import NORMAL
from tkinter import Tk

from app.main.frames import Frames
from app.main.layout import Layout
from app.main.ui_setter import UISetter
from app.main.vars import Variables
from const import Status
from helper.names import get_bom_export_name
from pytia.log import log
from pytia_ui_tools.handlers.workspace_handler import Workspace
from templates import templates
from ttkbootstrap import Style


class Traces:
    """The Traces class. Responsible for all variable traces in the main window."""

    def __init__(
        self,
        root: Tk,
        variables: Variables,
        state_setter: UISetter,
        frames: Frames,
        layout: Layout,
        style: Style,
        workspace: Workspace,
    ) -> None:
        """
        Inits the Traces class. Adds the main windows' variable traces.

        Args:
            vars (Variables): The main window's variables.
            state_setter (UISetter): The state setter of the main window.
            frames (Frames): The frames of the main window.
            layout (Layout): The layout of the main window.
            workspace (Workspace): The workspace.
        """
        self.root = root
        self.vars = variables
        self.set_ui = state_setter
        self.frames = frames
        self.layout = layout
        self.style = style
        self.workspace = workspace

        self._add_traces()
        log.info("Traces initialized.")

    def _add_traces(self) -> None:
        """Adds all traces."""
        self.vars.project.trace_add("write", self.trace_project)
        self.vars.bom_export_path.trace_add("write", self.trace_bom_export_path)
        self.vars.docket_export_path.trace_add("write", self.trace_docket_export_path)
        self.vars.documentation_export_path.trace_add(
            "write", self.trace_docu_export_path
        )
        self.vars.drawing_export_path.trace_add("write", self.trace_drawing_export_path)
        self.vars.stp_export_path.trace_add("write", self.trace_stp_export_path)
        self.vars.stl_export_path.trace_add("write", self.trace_stl_export_path)
        self.vars.jpg_export_path.trace_add("write", self.trace_jpg_export_path)
        self.vars.ignore_prefix_txt.trace_add("write", self.trace_ignore_prefix_txt)
        self.vars.show_report.trace_add("write", self.trace_show_report)

    def _validate_button_export(self) -> None:
        self.set_ui.set_button_export()

    def trace_project(self, *_) -> None:
        """Trace callback for the `project` StringVar. Handles the filename for the export path."""
        # Apply project number to the excel export path
        current_folder = Path(self.vars.bom_export_path.get()).parent
        if os.path.exists(current_folder):
            self.vars.bom_export_path.set(
                str(
                    WindowsPath(
                        current_folder,
                        get_bom_export_name(
                            workspace=self.workspace,
                            project=self.vars.project.get(),
                            machine=self.vars.machine.get(),
                        ),
                    )
                )
            )

        self._validate_button_export()

    # @default_color
    def trace_bom_export_path(self, *_) -> None:
        """
        Trace callback for the `bom_export_path` StringVar. Validates the path and sets the state
        of the export button accordingly to the path variable.
        """

        if (
            Path(self.vars.bom_export_path.get()).parent.exists()
            and os.path.isabs(Path(self.vars.bom_export_path.get()).parent)
            and ".xlsx" in self.vars.bom_export_path.get()
        ):
            self.layout.input_bom_export_path.configure(
                foreground=self.style.colors.fg  # type: ignore
            )
        else:
            self.layout.input_bom_export_path.configure(
                foreground=self.style.colors.danger  # type: ignore
            )

        self._validate_button_export()

    def trace_docket_export_path(self, *_) -> None:
        """
        Trace callback for the `docket_export_path` StringVar. Validates the path and sets the state
        of the checkbox accordingly to the path variable.
        """
        if (
            is_dir := bool(
                os.path.isdir(self.vars.docket_export_path.get())
                and os.path.isabs(self.vars.docket_export_path.get())
            )
            and templates.docket_path is not None
            and os.path.isfile(templates.docket_path)
        ):
            self.layout.checkbox_export_docket.configure(state=NORMAL)
            self.vars.export_docket.set(True)
        else:
            self.vars.export_docket.set(False)
            self.layout.checkbox_export_docket.configure(state=DISABLED)

        self.layout.input_docket_export_path.configure(
            foreground=self.style.colors.fg if is_dir else self.style.colors.danger  # type: ignore
        )

    def trace_docu_export_path(self, *_) -> None:
        """
        Trace callback for the `documentation_export_path` StringVar.
        Validates the path and sets the state of the checkbox accordingly to the path
        variable.
        """
        if (
            is_dir := bool(
                os.path.isdir(self.vars.documentation_export_path.get())
                and os.path.isabs(self.vars.documentation_export_path.get())
            )
            and templates.documentation_path is not None
            and os.path.isfile(templates.documentation_path)
        ):
            self.layout.checkbox_export_documentation.configure(state=NORMAL)
            self.vars.export_documentation.set(True)
        else:
            self.vars.export_documentation.set(False)
            self.layout.checkbox_export_documentation.configure(state=DISABLED)

        self.layout.input_documentation_export_path.configure(
            foreground=self.style.colors.fg if is_dir else self.style.colors.danger  # type: ignore
        )

    def trace_drawing_export_path(self, *_) -> None:
        """
        Trace callback for the `drawing_export_path` StringVar.
        Validates the path and sets the state of the checkbox accordingly to the path variable.
        """
        if os.path.isdir(self.vars.drawing_export_path.get()) and os.path.isabs(
            self.vars.drawing_export_path.get()
        ):
            self.layout.input_drawing_export_path.configure(
                foreground=self.style.colors.fg  # type: ignore
            )
            self.layout.checkbox_export_drawing.configure(state=NORMAL)
            self.vars.export_drawing.set(True)
        else:
            self.layout.input_drawing_export_path.configure(
                foreground=self.style.colors.danger  # type: ignore
            )
            self.vars.export_drawing.set(False)
            self.layout.checkbox_export_drawing.configure(state=DISABLED)

    def trace_stp_export_path(self, *_) -> None:
        """Trace callback for the `stp_export_path` StringVar. Validates the path and sets the state
        of the checkbox accordingly to the path variable.
        """
        if os.path.isdir(self.vars.stp_export_path.get()) and os.path.isabs(
            self.vars.stp_export_path.get()
        ):
            self.layout.input_stp_export_path.configure(
                foreground=self.style.colors.fg  # type: ignore
            )
            self.layout.checkbox_export_stp.configure(state=NORMAL)
            self.vars.export_stp.set(True)
        else:
            self.layout.input_stp_export_path.configure(
                foreground=self.style.colors.danger  # type: ignore
            )
            self.vars.export_stp.set(False)
            self.layout.checkbox_export_stp.configure(state=DISABLED)

    def trace_stl_export_path(self, *_) -> None:
        """Trace callback for the `stl_export_path` StringVar. Validates the path and sets the state
        of the checkbox accordingly to the path variable.
        """
        if os.path.isdir(self.vars.stl_export_path.get()) and os.path.isabs(
            self.vars.stl_export_path.get()
        ):
            self.layout.input_stl_export_path.configure(
                foreground=self.style.colors.fg  # type: ignore
            )
            self.layout.checkbox_export_stl.configure(state=NORMAL)
            self.vars.export_stl.set(True)
        else:
            self.layout.input_stl_export_path.configure(
                foreground=self.style.colors.danger  # type: ignore
            )
            self.vars.export_stl.set(False)
            self.layout.checkbox_export_stl.configure(state=DISABLED)

    def trace_jpg_export_path(self, *_) -> None:
        """Trace callback for the `jpg_export_path` StringVar. Validates the path and sets the state
        of the checkbox accordingly to the path variable.
        """
        if os.path.isdir(self.vars.jpg_export_path.get()) and os.path.isabs(
            self.vars.jpg_export_path.get()
        ):
            self.layout.input_jpg_export_path.configure(
                foreground=self.style.colors.fg  # type: ignore
            )
            self.layout.checkbox_export_jpg.configure(state=NORMAL)
            self.vars.export_jpg.set(True)
        else:
            self.layout.input_jpg_export_path.configure(
                foreground=self.style.colors.danger  # type: ignore
            )
            self.vars.export_jpg.set(False)
            self.layout.checkbox_export_jpg.configure(state=DISABLED)

    def trace_ignore_prefix_txt(self, *_) -> None:
        """Trace callback for the `ignore_prefix_txt` StringVar. Validates the input
        and sets the state of the checkbox accordingly to the variable."""
        if len(self.vars.ignore_prefix_txt.get()) > 0:
            self.vars.ignore_prefix.set(True)
            self.layout.checkbox_ignore_prefixed.configure(state=NORMAL)
        else:
            self.vars.ignore_prefix.set(False)
            self.layout.checkbox_ignore_prefixed.configure(state=DISABLED)

    def trace_show_report(self, *_) -> None:
        """
        Trace callback for the `show_report` BooleanVar. Toggle the frames accordingly to the value.
        """
        if self.vars.show_report.get():
            for item in self.vars.report.items:
                if item.status == Status.FAILED:
                    self.layout.tree_report_failed_items.insert(
                        "", "end", values=(item.partnumber,)
                    )

            self.frames.infrastructure.grid_remove()
            self.frames.paths.grid_remove()
            self.frames.export.grid_remove()
            self.frames.log.grid_remove()
            self.frames.footer.grid_remove()

            self.frames.report.grid()
            self.frames.report_footer.grid()
        else:
            self.layout.tree_report_failed_items.delete(
                *self.layout.tree_report_failed_items.get_children()
            )
            self.layout.tree_report_failed_props.delete(
                *self.layout.tree_report_failed_props.get_children()
            )

            self.frames.report.grid_remove()
            self.frames.report_footer.grid_remove()

            self.frames.infrastructure.grid()
            self.frames.paths.grid()
            self.frames.export.grid()
            self.frames.footer.grid()
