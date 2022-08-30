"""
    The layout of the app.
"""
from tkinter import DISABLED, HORIZONTAL, Tk, ttk

from app.main.frames import Frames
from app.main.vars import Variables


class Layout:
    """The layout class of the app, holds all widgets."""

    MARGIN_X = 10
    MARGIN_Y = 10

    def __init__(self, root: Tk, frames: Frames, variables: Variables) -> None:
        """
        Inits the Layout class. Creates and places the widgets of the main window.

        Args:
            root (Tk): The main window.
            frames (Frames): The frames of the main window.
            variables (Variables): The variables of the main window.
        """ """"""
        # region FRAME Infra ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # region project
        lbl_project = ttk.Label(frames.infrastructure, text="Project", width=18)
        lbl_project.grid(
            row=0,
            column=0,
            padx=(Layout.MARGIN_X, 15),
            pady=(Layout.MARGIN_Y, Layout.MARGIN_Y),
            sticky="nsew",
        )

        self._combo_project = ttk.Combobox(
            frames.infrastructure,
            values=[],
            textvariable=variables.project,
        )
        self._combo_project.grid(
            row=0,
            column=1,
            padx=(5, Layout.MARGIN_X),
            pady=(Layout.MARGIN_Y, Layout.MARGIN_Y),
            ipadx=2,
            ipady=2,
            sticky="nsew",
            columnspan=2,
        )
        # endregion

        # TODO: Add export-only-where-project-is-... option

        # endregion

        # region FRAME Paths ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # region bom export path
        lbl_bom_export_path = ttk.Label(
            frames.paths, text="Bill of Material File", width=18
        )
        lbl_bom_export_path.grid(
            row=0,
            column=0,
            padx=(Layout.MARGIN_X, 15),
            pady=(Layout.MARGIN_Y, 2),
            sticky="nsew",
        )

        self._entry_bom_export_path = ttk.Entry(
            frames.paths,
            textvariable=variables.bom_export_path,
            state=DISABLED,
        )
        self._entry_bom_export_path.grid(
            row=0,
            column=1,
            padx=(5, 2),
            pady=(Layout.MARGIN_Y, 2),
            ipadx=2,
            ipady=2,
            sticky="nsew",
        )

        self._btn_browse_bom_export_path = ttk.Button(
            frames.paths,
            text="...",
            width=4,
            state=DISABLED,
        )
        self._btn_browse_bom_export_path.grid(
            row=0,
            column=2,
            padx=(2, Layout.MARGIN_X),
            pady=(Layout.MARGIN_Y, 2),
            sticky="nsew",
        )
        # endregion

        # region docket export path
        lbl_docket_export_path = ttk.Label(frames.paths, text="Docket Folder", width=18)
        lbl_docket_export_path.grid(
            row=1,
            column=0,
            padx=(Layout.MARGIN_X, 15),
            pady=(2, 2),
            sticky="nsew",
        )

        self._entry_docket_export_path = ttk.Entry(
            frames.paths,
            textvariable=variables.docket_export_path,
            state=DISABLED,
        )
        self._entry_docket_export_path.grid(
            row=1,
            column=1,
            padx=(5, 2),
            pady=(2, 2),
            ipadx=2,
            ipady=2,
            sticky="nsew",
        )

        self._btn_browse_docket_export_path = ttk.Button(
            frames.paths,
            text="...",
            width=4,
            state=DISABLED,
        )
        self._btn_browse_docket_export_path.grid(
            row=1,
            column=2,
            padx=(2, Layout.MARGIN_X),
            pady=(2, 2),
            sticky="nsew",
        )
        # endregion

        # region stp export path
        lbl_stp_export_path = ttk.Label(frames.paths, text="STP Folder", width=18)
        lbl_stp_export_path.grid(
            row=2,
            column=0,
            padx=(Layout.MARGIN_X, 15),
            pady=(2, 2),
            sticky="nsew",
        )

        self._entry_stp_export_path = ttk.Entry(
            frames.paths,
            textvariable=variables.stp_export_path,
            state=DISABLED,
        )
        self._entry_stp_export_path.grid(
            row=2,
            column=1,
            padx=(5, 2),
            pady=(2, 2),
            ipadx=2,
            ipady=2,
            sticky="nsew",
        )

        self._btn_browse_stp_export_path = ttk.Button(
            frames.paths,
            text="...",
            width=4,
            state=DISABLED,
        )
        self._btn_browse_stp_export_path.grid(
            row=2,
            column=2,
            padx=(2, Layout.MARGIN_X),
            pady=(2, 2),
            sticky="nsew",
        )
        # endregion

        # region stl export path
        lbl_stl_export_path = ttk.Label(frames.paths, text="STL Folder", width=18)
        lbl_stl_export_path.grid(
            row=3,
            column=0,
            padx=(Layout.MARGIN_X, 15),
            pady=(2, Layout.MARGIN_Y),
            sticky="nsew",
        )

        self._entry_stl_export_path = ttk.Entry(
            frames.paths,
            textvariable=variables.stl_export_path,
            state=DISABLED,
        )
        self._entry_stl_export_path.grid(
            row=3,
            column=1,
            padx=(5, 2),
            pady=(2, Layout.MARGIN_Y),
            ipadx=2,
            ipady=2,
            sticky="nsew",
        )

        self._btn_browse_stl_export_path = ttk.Button(
            frames.paths,
            text="...",
            width=4,
            state=DISABLED,
        )
        self._btn_browse_stl_export_path.grid(
            row=3,
            column=2,
            padx=(2, Layout.MARGIN_X),
            pady=(2, Layout.MARGIN_Y),
            sticky="nsew",
        )
        # endregion

        # region FRAME Export ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # region export docket
        lbl_export_docket = ttk.Label(frames.export, text="Export Docket", width=18)
        lbl_export_docket.grid(
            row=0,
            column=0,
            padx=(Layout.MARGIN_X, 15),
            pady=(Layout.MARGIN_Y, 2),
            sticky="nsew",
        )

        self._chkbtn_export_docket = ttk.Checkbutton(
            frames.export, variable=variables.export_docket, state=DISABLED
        )
        self._chkbtn_export_docket.grid(
            row=0,
            column=1,
            padx=(5, 5),
            pady=(Layout.MARGIN_Y, 2),
            sticky="nsew",
        )
        # endregion

        # region export stp
        lbl_export_stp = ttk.Label(frames.export, text="Export STP", width=18)
        lbl_export_stp.grid(
            row=1,
            column=0,
            padx=(Layout.MARGIN_X, 15),
            pady=(2, 2),
            sticky="nsew",
        )

        self._chkbtn_export_stp = ttk.Checkbutton(
            frames.export, variable=variables.export_stp, state=DISABLED
        )
        self._chkbtn_export_stp.grid(
            row=1,
            column=1,
            padx=(5, 5),
            pady=(2, 2),
            sticky="nsew",
        )
        # endregion

        # region export stl
        lbl_export_stl = ttk.Label(frames.export, text="Export STL", width=18)
        lbl_export_stl.grid(
            row=2,
            column=0,
            padx=(Layout.MARGIN_X, 15),
            pady=(2, Layout.MARGIN_Y),
            sticky="nsew",
        )

        self._chkbtn_export_stl = ttk.Checkbutton(
            frames.export, variable=variables.export_stl, state=DISABLED
        )
        self._chkbtn_export_stl.grid(
            row=2,
            column=1,
            padx=(5, 5),
            pady=(2, Layout.MARGIN_Y),
            sticky="nsew",
        )
        # endregion
        # endregion

        # region FRAME Report ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        lbl_report = ttk.Label(frames.report, text="Foo", width=18)
        lbl_report.grid(
            row=0,
            column=0,
            padx=(Layout.MARGIN_X, 15),
            pady=(2, Layout.MARGIN_Y),
            sticky="nsew",
        )

        self._tree_report_failed_items = ttk.Treeview(
            frames.report, columns=("failed_items",), show="headings", height=10
        )
        self._tree_report_failed_items.heading("failed_items", text="Failed Items")
        self._tree_report_failed_items.column("failed_items", width=200, anchor="w")
        self._tree_report_failed_items.grid(
            row=0,
            column=0,
            padx=(Layout.MARGIN_X, 5),
            pady=Layout.MARGIN_Y,
            sticky="nsew",
            rowspan=4,
        )

        self._tree_report_failed_props = ttk.Treeview(
            frames.report, columns=("failed_props",), show="headings", height=10
        )
        self._tree_report_failed_props.heading("failed_props", text="Failed Properties")
        self._tree_report_failed_props.column("failed_props", width=200, anchor="w")
        self._tree_report_failed_props.grid(
            row=0,
            column=1,
            padx=(5, Layout.MARGIN_X),
            pady=(Layout.MARGIN_Y, 5),
            sticky="nsew",
        )

        self._btn_open_document = ttk.Button(
            frames.report, text="Open Document", style="Footer.TButton", state=DISABLED
        )
        self._btn_open_document.grid(
            row=1,
            column=1,
            padx=(5, Layout.MARGIN_X),
            pady=(5, 2),
            sticky="sew",
        )

        self._btn_open_parent = ttk.Button(
            frames.report, text="Open Parent", style="Footer.TButton", state=DISABLED
        )
        self._btn_open_parent.grid(
            row=2,
            column=1,
            padx=(5, Layout.MARGIN_X),
            pady=(2, 2),
            sticky="sew",
        )

        self._btn_close_document = ttk.Button(
            frames.report, text="Close Document", style="Footer.TButton", state=DISABLED
        )
        self._btn_close_document.grid(
            row=3,
            column=1,
            padx=(5, Layout.MARGIN_X),
            pady=(2, Layout.MARGIN_Y),
            sticky="sew",
        )

        self._btn_close_report = ttk.Button(
            frames.report_footer, text="Close", style="Footer.TButton"
        )
        self._btn_close_report.grid(row=0, column=0, padx=(2, 0), pady=0, sticky="e")
        # endregion

        # region FRAME Footer ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # region progress
        self._progress_bar = ttk.Progressbar(
            frames.footer,
            orient=HORIZONTAL,
            length=100,
            mode="determinate",
            variable=variables.progress,
        )
        self._progress_bar.grid(
            row=0, column=0, padx=(1, 5), pady=(1, 1), sticky="nsew"
        )
        self._progress_bar.grid_remove()

        # endregion

        # region button save
        self._btn_export = ttk.Button(
            frames.footer, text="Export", style="Footer.TButton", state=DISABLED
        )
        self._btn_export.grid(row=0, column=1, padx=(5, 2), pady=0, sticky="e")
        # endregion

        # region button abort
        self._btn_exit = ttk.Button(frames.footer, text="Exit", style="Footer.TButton")
        self._btn_exit.grid(row=0, column=2, padx=(2, 0), pady=0, sticky="e")
        # endregion
        # endregion

    @property
    def input_project(self) -> ttk.Combobox:
        """Returns the project combobox."""
        return self._combo_project

    @property
    def input_bom_export_path(self) -> ttk.Entry:
        return self._entry_bom_export_path

    @property
    def button_bom_export_path(self) -> ttk.Button:
        return self._btn_browse_bom_export_path

    @property
    def input_docket_export_path(self) -> ttk.Entry:
        return self._entry_docket_export_path

    @property
    def button_docket_export_path(self) -> ttk.Button:
        return self._btn_browse_docket_export_path

    @property
    def input_stp_export_path(self) -> ttk.Entry:
        return self._entry_stp_export_path

    @property
    def button_stp_export_path(self) -> ttk.Button:
        return self._btn_browse_stp_export_path

    @property
    def input_stl_export_path(self) -> ttk.Entry:
        return self._entry_stl_export_path

    @property
    def button_stl_export_path(self) -> ttk.Button:
        return self._btn_browse_stl_export_path

    @property
    def checkbox_export_docket(self) -> ttk.Checkbutton:
        return self._chkbtn_export_docket

    @property
    def checkbox_export_stp(self) -> ttk.Checkbutton:
        return self._chkbtn_export_stp

    @property
    def checkbox_export_stl(self) -> ttk.Checkbutton:
        return self._chkbtn_export_stl

    @property
    def progress_bar(self) -> ttk.Progressbar:
        return self._progress_bar

    @property
    def tree_report_failed_items(self) -> ttk.Treeview:
        return self._tree_report_failed_items

    @property
    def tree_report_failed_props(self) -> ttk.Treeview:
        return self._tree_report_failed_props

    @property
    def button_export(self) -> ttk.Button:
        """Returns the export button."""
        return self._btn_export

    @property
    def button_open_document(self) -> ttk.Button:
        """Returns the open document button."""
        return self._btn_open_document

    @property
    def button_open_parent(self) -> ttk.Button:
        """Returns the open parent button."""
        return self._btn_open_parent

    @property
    def button_close_document(self) -> ttk.Button:
        """Returns the close document button."""
        return self._btn_close_document

    @property
    def button_exit(self) -> ttk.Button:
        """Returns the exit button."""
        return self._btn_exit

    @property
    def button_close_report(self) -> ttk.Button:
        """Returns the close report button."""
        return self._btn_close_report