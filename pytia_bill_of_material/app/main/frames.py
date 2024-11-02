"""
    Frames submodule for the main window.
"""

from tkinter import Tk

from ttkbootstrap import Frame
from ttkbootstrap import Labelframe
from ttkbootstrap.scrolled import ScrolledFrame


class Frames:
    """Frames class for the main window. Holds all ttk frames."""

    def __init__(self, root: Tk) -> None:
        self._frame_infra = Labelframe(master=root, text="Infrastructure")
        self._frame_infra.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=(10, 5))
        self._frame_infra.grid_columnconfigure(1, weight=1)
        # self._frame_infra.grid_remove()

        self._frame_paths = Labelframe(master=root, text="Paths")
        self._frame_paths.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(5, 5))
        self._frame_paths.grid_columnconfigure(1, weight=1)
        # self._frame_paths.grid_remove()

        self._frame_export = Labelframe(master=root, text="Export")
        self._frame_export.grid(row=2, column=0, sticky="nsew", padx=(10, 5), pady=(5, 10))
        self._frame_export.grid_columnconfigure(6, weight=1)
        # self._frame_export.grid_remove()

        self._frame_filters_wrapper = Labelframe(master=root, text="Filters")
        self._frame_filters_wrapper.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=(10, 10), rowspan=3)
        self._frame_filters_wrapper.grid_rowconfigure(0, weight=1)
        self._frame_filters_wrapper.grid_columnconfigure(0, weight=1)

        self._frame_filters_elements = ScrolledFrame(master=self._frame_filters_wrapper, autohide=True, padding=10)
        self._frame_filters_elements.grid(row=0, column=0, sticky="nsew")
        self._frame_filters_elements.grid_rowconfigure(0, weight=1)
        self._frame_filters_elements.grid_columnconfigure(0, weight=1)

        self._frame_report = Labelframe(master=root, text="Report")
        self._frame_report.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(10, 10),
            pady=(5, 10),
            columnspan=2,
            rowspan=3,
        )
        self._frame_report.grid_rowconfigure(0, weight=1)
        self._frame_report.grid_columnconfigure(0, weight=1)
        self._frame_report.grid_columnconfigure(1, weight=1)
        self._frame_report.grid_remove()

        self._frame_report_footer = Frame(master=root, height=30)
        self._frame_report_footer.grid(row=4, column=0, sticky="swe", padx=10, pady=(5, 10), columnspan=2)
        self._frame_report_footer.grid_columnconfigure(0, weight=1)
        self._frame_report_footer.grid_remove()

        self._frame_log = Labelframe(master=root, text="Log")
        self._frame_log.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(10, 10),
            pady=(5, 10),
            columnspan=2,
            rowspan=3,
        )
        self._frame_log.grid_columnconfigure(0, weight=1)
        self._frame_log.grid_rowconfigure(0, weight=1)
        self._frame_log.grid_remove()

        self._frame_footer = Frame(master=root, height=30)
        self._frame_footer.grid(row=4, column=0, sticky="swe", padx=10, pady=(5, 10), columnspan=2)
        self._frame_footer.grid_columnconfigure(0, weight=1)

        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        # root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)

    @property
    def infrastructure(self) -> Labelframe:
        """Returns the infrastructure frame."""
        return self._frame_infra

    @property
    def paths(self) -> Labelframe:
        """Returns the paths frame."""
        return self._frame_paths

    @property
    def export(self) -> Labelframe:
        """Returns the export frame."""
        return self._frame_export

    @property
    def filters(self) -> Labelframe:
        """Returns the filters frame."""
        return self._frame_filters_wrapper

    @property
    def filter_elements(self) -> ScrolledFrame:
        """Returns the filter elements."""
        return self._frame_filters_elements

    @property
    def report(self) -> Labelframe:
        """Returns the report frame."""
        return self._frame_report

    @property
    def log(self) -> Labelframe:
        """Returns the log frame."""
        return self._frame_log

    @property
    def footer(self) -> Frame:
        """Returns the footer frame."""
        return self._frame_footer

    @property
    def report_footer(self) -> Frame:
        """Returns the report footer frame."""
        return self._frame_report_footer
