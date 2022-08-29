"""
    Frames submodule for the main window.
"""

from tkinter import Tk, ttk


class Frames:
    """Frames class for the main window. Holds all ttk frames."""

    def __init__(self, root: Tk) -> None:
        self._frame_infra = ttk.Labelframe(
            master=root, style="Infrastructure.TLabelframe", text="Infrastructure"
        )
        self._frame_infra.grid(
            row=0, column=0, sticky="nsew", padx=(10, 10), pady=(10, 5)
        )
        self._frame_infra.grid_columnconfigure(1, weight=1)
        # self._frame_infra.grid_remove()

        self._frame_paths = ttk.Labelframe(
            master=root, style="Paths.TLabelframe", text="Paths"
        )
        self._frame_paths.grid(
            row=1, column=0, sticky="nsew", padx=(10, 10), pady=(5, 5)
        )
        self._frame_paths.grid_columnconfigure(1, weight=1)
        # self._frame_paths.grid_remove()

        self._frame_export = ttk.Labelframe(
            master=root, style="Export.TLabelframe", text="Export"
        )
        self._frame_export.grid(
            row=2, column=0, sticky="nsew", padx=(10, 10), pady=(5, 10)
        )
        self._frame_export.grid_columnconfigure(1, weight=1)
        # self._frame_export.grid_remove()

        self._frame_report = ttk.Labelframe(
            master=root, style="Report.TLabelframe", text="Report"
        )
        self._frame_report.grid(
            row=0, column=0, sticky="nsew", padx=(10, 10), pady=(5, 10)
        )
        self._frame_report.grid_rowconfigure(0, weight=1)
        self._frame_report.grid_columnconfigure(0, weight=1)
        self._frame_report.grid_columnconfigure(1, weight=1)
        self._frame_report.grid_remove()

        self._frame_report_footer = ttk.Frame(
            master=root, height=30, style="Footer.TFrame"
        )
        self._frame_report_footer.grid(
            row=1, column=0, sticky="swe", padx=10, pady=(5, 10)
        )
        self._frame_report_footer.grid_columnconfigure(0, weight=1)
        self._frame_report_footer.grid_remove()

        self._frame_footer = ttk.Frame(master=root, height=30, style="Footer.TFrame")
        self._frame_footer.grid(row=4, column=0, sticky="swe", padx=10, pady=(5, 10))
        self._frame_footer.grid_columnconfigure(0, weight=1)

        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)

    @property
    def infrastructure(self) -> ttk.Labelframe:
        """Returns the infrastructure frame."""
        return self._frame_infra

    @property
    def paths(self) -> ttk.Labelframe:
        """Returns the paths frame."""
        return self._frame_paths

    @property
    def export(self) -> ttk.Labelframe:
        """Returns the export frame."""
        return self._frame_export

    @property
    def report(self) -> ttk.Labelframe:
        """Returns the report frame."""
        return self._frame_report

    @property
    def footer(self) -> ttk.Frame:
        """Returns the footer frame."""
        return self._frame_footer

    @property
    def report_footer(self) -> ttk.Frame:
        """Returns the report footer frame."""
        return self._frame_report_footer
