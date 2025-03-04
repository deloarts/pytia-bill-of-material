"""
    The layout of the app.
"""

# pylint: disable=C0116

from tkinter import DISABLED
from tkinter import HORIZONTAL
from tkinter import WORD
from tkinter import BooleanVar
from tkinter import Text
from tkinter import Tk
from tkinter import messagebox as tkmsg

from app.main.frames import Frames
from app.main.vars import Variables
from const import STYLES
from helper.appearance import set_appearance_menu
from helper.files import set_external_bom_file
from helper.messages import show_help
from pytia_ui_tools.handlers.workspace_handler import Workspace
from pytia_ui_tools.widgets.tooltips import ToolTip
from resources import resource
from ttkbootstrap import Button
from ttkbootstrap import Checkbutton
from ttkbootstrap import Combobox
from ttkbootstrap import Entry
from ttkbootstrap import Label
from ttkbootstrap import Menu
from ttkbootstrap import Progressbar
from ttkbootstrap import Treeview
from worker.prepare import PrepareTask


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
        """
        self._root = root
        self._frames = frames
        self._variables = variables

        # region FRAME Infra ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # region MENU
        menubar = Menu(root)

        self._appearance_menu = Menu(menubar, tearoff=False)
        for style in STYLES:
            self._appearance_menu.add_command(label=style)

        self._tools_menu = Menu(menubar, tearoff=False)
        self._tools_menu.add_command(label="Set BOM Format", command=PrepareTask.set_catia_bom_format)
        self._tools_menu.add_command(
            label="Set external BOM",
            command=lambda: set_external_bom_file(root, variables),
        )

        menubar.add_cascade(label="Help", command=show_help)
        menubar.add_cascade(label="Appearance", menu=self._appearance_menu)
        menubar.add_cascade(label="Tools", menu=self._tools_menu)

        set_appearance_menu(self._appearance_menu)
        root.configure(menu=menubar)
        # endregion

        # region project
        lbl_project = Label(frames.infrastructure, text="Project", width=18)
        lbl_project.grid(
            row=0,
            column=0,
            padx=(Layout.MARGIN_X, 15),
            pady=(Layout.MARGIN_Y, Layout.MARGIN_Y),
            sticky="nsew",
        )

        self._combo_project = Combobox(
            frames.infrastructure,
            textvariable=variables.project,
            state=DISABLED,
        )
        self._combo_project.grid(
            row=0,
            column=1,
            padx=(5, Layout.MARGIN_X),
            pady=(Layout.MARGIN_Y, Layout.MARGIN_Y),
            sticky="nsew",
            columnspan=2,
        )
        # endregion

        # TODO: Add export-only-where-project-is-... option

        # endregion

        # region bom export path
        lbl_bom_export_path = Label(frames.paths, text="Bill of Material File", width=18)
        lbl_bom_export_path.grid(
            row=0,
            column=0,
            padx=(Layout.MARGIN_X, 15),
            pady=(Layout.MARGIN_Y, 2),
            sticky="nsew",
        )

        self._entry_bom_export_path = Entry(
            frames.paths,
            textvariable=variables.bom_export_path,
            state=DISABLED,
        )
        self._entry_bom_export_path.grid(
            row=0,
            column=1,
            padx=(5, 2),
            pady=(Layout.MARGIN_Y, 2),
            sticky="nsew",
        )

        self._btn_browse_bom_export_path = Button(
            frames.paths,
            text="...",
            style="outline",
            width=3,
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

        # region documentation export path
        lbl_docu_export_path = Label(frames.paths, text="Docs Folder", width=18)
        lbl_docu_export_path.grid(
            row=1,
            column=0,
            padx=(Layout.MARGIN_X, 15),
            pady=(2, 2),
            sticky="nsew",
        )

        self._entry_docu_export_path = Entry(
            frames.paths,
            textvariable=variables.documentation_export_path,
            state=DISABLED,
        )
        self._entry_docu_export_path.grid(
            row=1,
            column=1,
            padx=(5, 2),
            pady=(2, 2),
            sticky="nsew",
        )

        self._btn_browse_docu_export_path = Button(
            frames.paths,
            text="...",
            style="outline",
            width=3,
            state=DISABLED,
        )
        self._btn_browse_docu_export_path.grid(
            row=1,
            column=2,
            padx=(2, Layout.MARGIN_X),
            pady=(2, 2),
            sticky="nsew",
        )
        # endregion

        # region docket export path
        self._lbl_docket_export_path = Label(frames.paths, text="Docket Folder", width=18)
        self._lbl_docket_export_path.grid(
            row=2,
            column=0,
            padx=(Layout.MARGIN_X, 15),
            pady=(2, 2),
            sticky="nsew",
        )

        self._entry_docket_export_path = Entry(
            frames.paths,
            textvariable=variables.docket_export_path,
            state=DISABLED,
        )
        self._entry_docket_export_path.grid(
            row=2,
            column=1,
            padx=(5, 2),
            pady=(2, 2),
            sticky="nsew",
        )

        self._btn_browse_docket_export_path = Button(
            frames.paths,
            text="...",
            style="outline",
            width=3,
            state=DISABLED,
        )
        self._btn_browse_docket_export_path.grid(
            row=2,
            column=2,
            padx=(2, Layout.MARGIN_X),
            pady=(2, 2),
            sticky="nsew",
        )
        # endregion

        # region drawing export path
        self._lbl_drawing_export_path = Label(frames.paths, text="Drawing Folder", width=18)
        self._lbl_drawing_export_path.grid(
            row=3,
            column=0,
            padx=(Layout.MARGIN_X, 15),
            pady=(2, 2),
            sticky="nsew",
        )

        self._entry_drawing_export_path = Entry(
            frames.paths,
            textvariable=variables.drawing_export_path,
            state=DISABLED,
        )
        self._entry_drawing_export_path.grid(
            row=3,
            column=1,
            padx=(5, 2),
            pady=(2, 2),
            sticky="nsew",
        )

        self._btn_browse_drawing_export_path = Button(
            frames.paths,
            text="...",
            style="outline",
            width=3,
            state=DISABLED,
        )
        self._btn_browse_drawing_export_path.grid(
            row=3,
            column=2,
            padx=(2, Layout.MARGIN_X),
            pady=(2, 2),
            sticky="nsew",
        )
        # endregion

        # region stp export path
        self._lbl_stp_export_path = Label(frames.paths, text="STP Folder", width=18)
        self._lbl_stp_export_path.grid(
            row=4,
            column=0,
            padx=(Layout.MARGIN_X, 15),
            pady=(2, 2),
            sticky="nsew",
        )

        self._entry_stp_export_path = Entry(
            frames.paths,
            textvariable=variables.stp_export_path,
            state=DISABLED,
        )
        self._entry_stp_export_path.grid(
            row=4,
            column=1,
            padx=(5, 2),
            pady=(2, 2),
            sticky="nsew",
        )

        self._btn_browse_stp_export_path = Button(
            frames.paths,
            text="...",
            style="outline",
            width=3,
            state=DISABLED,
        )
        self._btn_browse_stp_export_path.grid(
            row=4,
            column=2,
            padx=(2, Layout.MARGIN_X),
            pady=(2, 2),
            sticky="nsew",
        )
        # endregion

        # region stl export path
        self._lbl_stl_export_path = Label(frames.paths, text="STL Folder", width=18)
        self._lbl_stl_export_path.grid(
            row=5,
            column=0,
            padx=(Layout.MARGIN_X, 15),
            pady=(2, 2),
            sticky="nsew",
        )

        self._entry_stl_export_path = Entry(
            frames.paths,
            textvariable=variables.stl_export_path,
            state=DISABLED,
        )
        self._entry_stl_export_path.grid(
            row=5,
            column=1,
            padx=(5, 2),
            pady=(2, 2),
            sticky="nsew",
        )

        self._btn_browse_stl_export_path = Button(
            frames.paths,
            text="...",
            style="outline",
            width=3,
            state=DISABLED,
        )
        self._btn_browse_stl_export_path.grid(
            row=5,
            column=2,
            padx=(2, Layout.MARGIN_X),
            pady=(2, 2),
            sticky="nsew",
        )
        # endregion

        # region jpg export path
        self._lbl_jpg_export_path = Label(frames.paths, text="JPG Folder", width=18)
        self._lbl_jpg_export_path.grid(
            row=6,
            column=0,
            padx=(Layout.MARGIN_X, 15),
            pady=(2, Layout.MARGIN_Y),
            sticky="nsew",
        )

        self._entry_jpg_export_path = Entry(
            frames.paths,
            textvariable=variables.jpg_export_path,
            state=DISABLED,
        )
        self._entry_jpg_export_path.grid(
            row=6,
            column=1,
            padx=(5, 2),
            pady=(2, Layout.MARGIN_Y),
            sticky="nsew",
        )

        self._btn_browse_jpg_export_path = Button(
            frames.paths,
            text="...",
            style="outline",
            width=3,
            state=DISABLED,
        )
        self._btn_browse_jpg_export_path.grid(
            row=6,
            column=2,
            padx=(2, Layout.MARGIN_X),
            pady=(2, Layout.MARGIN_Y),
            sticky="nsew",
        )
        # endregion

        # region bundle export path
        self._lbl_bundle_export_path = Label(frames.paths, text="Bundle Folder", width=18)
        self._lbl_bundle_export_path.grid(
            row=7,
            column=0,
            padx=(Layout.MARGIN_X, 15),
            pady=(2, Layout.MARGIN_Y),
            sticky="nsew",
        )
        self._lbl_bundle_export_path.grid_remove()

        self._entry_bundle_export_path = Entry(
            frames.paths,
            textvariable=variables.bundle_export_path,
            state=DISABLED,
        )
        self._entry_bundle_export_path.grid(
            row=7,
            column=1,
            padx=(5, 2),
            pady=(2, Layout.MARGIN_Y),
            sticky="nsew",
        )
        self._entry_bundle_export_path.grid_remove()

        self._btn_browse_bundle_export_path = Button(
            frames.paths,
            text="...",
            style="outline",
            width=3,
            state=DISABLED,
        )
        self._btn_browse_bundle_export_path.grid(
            row=7,
            column=2,
            padx=(2, Layout.MARGIN_X),
            pady=(2, Layout.MARGIN_Y),
            sticky="nsew",
        )
        self._btn_browse_bundle_export_path.grid_remove()
        # endregion

        # region FRAME Export ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # region export documentation docket
        self._chkbtn_export_documentation = Checkbutton(
            frames.export,
            bootstyle="round-toggle",  # type:ignore
            variable=variables.export_documentation,
            state=DISABLED,
        )
        self._chkbtn_export_documentation.grid(
            row=0,
            column=0,
            padx=(16, 2),
            pady=(Layout.MARGIN_Y, 2),
            sticky="nsew",
        )
        lbl_export_documentation = Label(frames.export, text="Export Docu", width=19)
        lbl_export_documentation.grid(
            row=0,
            column=1,
            padx=(2, 5),
            pady=(Layout.MARGIN_Y, 2),
            sticky="nsw",
        )
        # endregion

        # region export docket
        self._chkbtn_export_docket = Checkbutton(
            frames.export,
            bootstyle="round-toggle",  # type:ignore
            variable=variables.export_docket,
            state=DISABLED,
        )
        self._chkbtn_export_docket.grid(
            row=0,
            column=2,
            padx=(5, 2),
            pady=(Layout.MARGIN_Y, 2),
            sticky="nsw",
        )
        lbl_export_docket = Label(frames.export, text="Export Docket", width=19)
        lbl_export_docket.grid(
            row=0,
            column=3,
            padx=(2, 5),
            pady=(Layout.MARGIN_Y, 2),
            sticky="nsw",
        )
        # endregion

        # region export drawing
        self._chkbtn_export_drawing = Checkbutton(
            frames.export,
            bootstyle="round-toggle",  # type:ignore
            variable=variables.export_drawing,
            state=DISABLED,
        )
        self._chkbtn_export_drawing.grid(
            row=0,
            column=4,
            padx=(5, 2),
            pady=(Layout.MARGIN_Y, 2),
            sticky="nsw",
        )
        lbl_export_drawing = Label(frames.export, text="Export Drawing", width=19)
        lbl_export_drawing.grid(
            row=0,
            column=5,
            padx=(2, 5),
            pady=(Layout.MARGIN_Y, 2),
            sticky="nsw",
        )
        # endregion

        # region export stp
        self._chkbtn_export_stp = Checkbutton(
            frames.export,
            bootstyle="round-toggle",  # type:ignore
            variable=variables.export_stp,
            state=DISABLED,
        )
        self._chkbtn_export_stp.grid(
            row=1,
            column=0,
            padx=(16, 2),
            pady=(2, 2),
            sticky="nsw",
        )
        lbl_export_stp = Label(frames.export, text="Export STP", width=19)
        lbl_export_stp.grid(
            row=1,
            column=1,
            padx=(2, 5),
            pady=(2, 2),
            sticky="nsw",
        )
        # endregion

        # region export stl
        self._chkbtn_export_stl = Checkbutton(
            frames.export,
            bootstyle="round-toggle",  # type:ignore
            variable=variables.export_stl,
            state=DISABLED,
        )
        self._chkbtn_export_stl.grid(
            row=1,
            column=2,
            padx=(5, 2),
            pady=(2, 2),
            sticky="nsw",
        )
        lbl_export_stl = Label(frames.export, text="Export STL", width=19)
        lbl_export_stl.grid(
            row=1,
            column=3,
            padx=(2, 5),
            pady=(2, 2),
            sticky="nsw",
        )
        # endregion

        # region export jpg
        self._chkbtn_export_jpg = Checkbutton(
            frames.export,
            bootstyle="round-toggle",  # type:ignore
            variable=variables.export_jpg,
            state=DISABLED,
        )
        self._chkbtn_export_jpg.grid(
            row=1,
            column=4,
            padx=(5, 2),
            pady=(2, 2),
            sticky="nsw",
        )
        lbl_export_jpg = Label(frames.export, text="Export JPG", width=19)
        lbl_export_jpg.grid(
            row=1,
            column=5,
            padx=(2, 5),
            pady=(2, 2),
            sticky="nsw",
        )
        # endregion

        # region Bundle
        self._chkbtn_bundle_data = Checkbutton(
            frames.export,
            bootstyle="round-toggle",  # type:ignore
            variable=variables.bundle,
            state=DISABLED,
        )
        self._chkbtn_bundle_data.grid(
            row=2,
            column=0,
            padx=(16, 2),
            pady=(20, 2),
            sticky="nsew",
            columnspan=2,
        )
        lbl_bundle_option = Label(frames.export, text="Bundle Data", width=19)
        lbl_bundle_option.grid(
            row=2,
            column=1,
            padx=(2, 5),
            pady=(20, 2),
            sticky="nsew",
        )

        self._chkbtn_bundle_zip = Checkbutton(
            frames.export,
            bootstyle="round-toggle",  # type:ignore
            variable=variables.zip_bundle,
            state=DISABLED,
        )
        self._chkbtn_bundle_zip.grid(
            row=2,
            column=2,
            padx=(5, 2),
            pady=(20, 2),
            sticky="nsew",
            columnspan=2,
        )
        lbl_bundle_zip_option = Label(frames.export, text="ZIP Bundle", width=19)
        lbl_bundle_zip_option.grid(
            row=2,
            column=3,
            padx=(2, 5),
            pady=(20, 2),
            sticky="nsew",
        )

        self._chkbtn_bundle_by_prop = Checkbutton(
            frames.export,
            bootstyle="round-toggle",  # type:ignore
            variable=variables.bundle_by_prop,
            state=DISABLED,
        )
        self._chkbtn_bundle_by_prop.grid(
            row=2,
            column=4,
            padx=(5, 2),
            pady=(20, 2),
            sticky="nsw",
        )
        lbl_bundle_by_prop = Label(frames.export, text="Bundle by property:", width=19)
        lbl_bundle_by_prop.grid(
            row=2,
            column=5,
            padx=(2, 5),
            pady=(20, 2),
            sticky="nsw",
        )
        self._combo_bundle_by_prop = Combobox(
            frames.export,
            textvariable=variables.bundle_by_prop_txt,
            state=DISABLED,
        )
        self._combo_bundle_by_prop.grid(
            row=2,
            column=6,
            padx=(2, Layout.MARGIN_X),
            pady=(20, 2),
            sticky="nsew",
            columnspan=2,
        )
        # self._entry_bundle_by_prop = Entry(
        #     frames.export,
        #     textvariable=variables.bundle_by_prop_txt,
        #     state=DISABLED,
        # )
        # self._entry_bundle_by_prop.grid(
        #     row=2,
        #     column=6,
        #     padx=(2, Layout.MARGIN_X),
        #     pady=(20, 2),
        #     sticky="nsew",
        #     columnspan=2,
        # )
        # endregion

        # region ignore source "unknown"
        self._chkbtn_ignore_unknown = Checkbutton(
            frames.export,
            bootstyle="round-toggle",  # type:ignore
            variable=variables.ignore_source_unknown,
            state=DISABLED,
        )
        self._chkbtn_ignore_unknown.grid(
            row=3,
            column=2,
            padx=(5, 2),
            pady=(20, Layout.MARGIN_Y),
            sticky="nsw",
        )
        lbl_ignore_unknown = Label(frames.export, text="Ignore Unknown", width=19)
        lbl_ignore_unknown.grid(
            row=3,
            column=3,
            padx=(2, 5),
            pady=(20, Layout.MARGIN_Y),
            sticky="nsw",
        )
        # endregion

        # region ignore prefix
        self._chkbtn_ignore_prefixed = Checkbutton(
            frames.export,
            bootstyle="round-toggle",  # type:ignore
            variable=variables.ignore_prefix,
            state=DISABLED,
        )
        self._chkbtn_ignore_prefixed.grid(
            row=3,
            column=4,
            padx=(5, 2),
            pady=(20, Layout.MARGIN_Y),
            sticky="nsw",
        )
        lbl_ignore_prefixed = Label(frames.export, text="Ignore Prefixed with:", width=19)
        lbl_ignore_prefixed.grid(
            row=3,
            column=5,
            padx=(2, 5),
            pady=(20, Layout.MARGIN_Y),
            sticky="nsw",
        )
        self._entry_ignore_prefix_txt = Entry(
            frames.export,
            textvariable=variables.ignore_prefix_txt,
            state=DISABLED,
        )
        self._entry_ignore_prefix_txt.grid(
            row=3,
            column=6,
            padx=(2, Layout.MARGIN_X),
            pady=(20, Layout.MARGIN_Y),
            sticky="nsew",
            columnspan=2,
        )
        # endregion
        # endregion

        # region FRAME Report ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        lbl_report = Label(frames.report, text="Report", width=18)
        lbl_report.grid(
            row=0,
            column=0,
            padx=(Layout.MARGIN_X, 15),
            pady=(2, Layout.MARGIN_Y),
            sticky="nsew",
        )

        self._tree_report_failed_items = Treeview(
            frames.report,
            columns=("failed_items", "parent"),
            show="headings",
            height=10,
        )
        self._tree_report_failed_items.heading("failed_items", text="Failed Items")
        self._tree_report_failed_items.heading("parent", text="Parent Assembly")
        self._tree_report_failed_items.column("failed_items", width=100, anchor="w")
        self._tree_report_failed_items.column("parent", width=100, anchor="w")
        self._tree_report_failed_items.grid(
            row=0,
            column=0,
            padx=(Layout.MARGIN_X, 5),
            pady=Layout.MARGIN_Y,
            sticky="nsew",
            rowspan=5,
        )

        self._tree_report_failed_props = Treeview(
            frames.report,
            columns=("failed_props", "user_ref_prop"),
            show="headings",
            height=10,
        )
        self._tree_report_failed_props.heading("failed_props", text="Failed Properties")
        self._tree_report_failed_props.heading("user_ref_prop", text="Property Name")
        self._tree_report_failed_props.column("failed_props", width=100, anchor="w")
        self._tree_report_failed_props.column("user_ref_prop", width=100, anchor="w")
        self._tree_report_failed_props.grid(
            row=0,
            column=1,
            padx=(5, Layout.MARGIN_X),
            pady=(Layout.MARGIN_Y, 5),
            sticky="nsew",
        )

        self._text_description = Text(
            frames.report,
            height=5,
            width=1,
            state=DISABLED,
            cursor="arrow",
            font=("Segoe UI", 9),
            wrap=WORD,
        )
        self._text_description.grid(row=1, column=1, padx=(5, Layout.MARGIN_X), pady=(5, 5), sticky="sew")

        self._btn_open_document = Button(frames.report, text="Open Document", style="outline", state=DISABLED)
        self._btn_open_document.grid(
            row=2,
            column=1,
            padx=(5, Layout.MARGIN_X),
            pady=(5, 2),
            sticky="sew",
        )

        self._btn_open_parent = Button(frames.report, text="Open Parent", style="outline", state=DISABLED)
        self._btn_open_parent.grid(
            row=3,
            column=1,
            padx=(5, Layout.MARGIN_X),
            pady=(2, 2),
            sticky="sew",
        )

        self._btn_close_document = Button(frames.report, text="Close Document", style="outline", state=DISABLED)
        self._btn_close_document.grid(
            row=4,
            column=1,
            padx=(5, Layout.MARGIN_X),
            pady=(2, Layout.MARGIN_Y),
            sticky="sew",
        )

        self._btn_close_report = Button(
            frames.report_footer,
            text="Close",
            style="outline",
            width=10,
        )
        self._btn_close_report.grid(row=0, column=0, padx=(2, 0), pady=0, sticky="e")
        # endregion

        # region FRAME Log  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self._text_log = Text(
            frames.log,
            height=1,
            width=1,
            state=DISABLED,
            cursor="arrow",
            font=("Monospac821 BT", 7),
            background="#f0f0f0",
            highlightthickness=0,
            borderwidth=0,
            wrap="none",
        )
        self._text_log.grid(row=0, column=0, padx=(5, 5), pady=(5, 5), sticky="nsew")
        # endregion

        # region FRAME Footer ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # region progress
        self._progress_bar = Progressbar(
            frames.footer,
            orient=HORIZONTAL,
            length=100,
            mode="determinate",
            variable=variables.progress,
        )
        self._progress_bar.grid(row=0, column=0, padx=(1, 5), pady=(1, 1), sticky="nsew")
        self._progress_bar.grid_remove()

        # endregion

        # region button save
        self._btn_export = Button(
            frames.footer,
            text="Export",
            style="outline",
            width=10,
            state=DISABLED,
        )
        self._btn_export.grid(row=0, column=1, padx=(5, 2), pady=0, sticky="e")
        # endregion

        # region button abort
        self._btn_exit = Button(
            frames.footer,
            text="Exit",
            style="outline",
            width=10,
        )
        self._btn_exit.grid(row=0, column=2, padx=(2, 0), pady=0, sticky="e")
        # endregion
        # endregion

    def add_filters(self, workspace: Workspace) -> None:
        """Adds filter toggles to the window. Uses all items from the filter.json file"""
        for index, filter_element in enumerate(resource.filters):
            filter_element._enabled = BooleanVar(master=self._root, value=True, name=f"filter_element_{index}")

            self._chkbtn_filter_element = Checkbutton(
                self._frames.filter_elements,
                bootstyle="round-toggle",  # type:ignore
                text=f"  {filter_element.name}",
                variable=filter_element._enabled,
            )
            self._chkbtn_filter_element.grid(
                row=index,
                column=0,
                padx=(6, 6),
                pady=(10, 10),
                sticky="nsw",
            )
            ToolTip(widget=self._chkbtn_filter_element, text=filter_element.description)

            if filter_element.criteria.startswith("%WS:"):
                workspace_element = filter_element.criteria.split("%WS:")[-1]
                if not workspace.available:
                    tkmsg.showwarning(
                        resource.settings.title,
                        f"The filter '{filter_element.name}' depends on the workspace "
                        "file, but there is no workspace file found. Please create "
                        "it.\n\nThe corresponding filter will be disabled for now.",
                    )
                    filter_element._enabled.set(False)
                elif (
                    not workspace_element in workspace.elements.__dict__
                    or workspace.elements.__dict__[workspace_element] is None
                ):
                    tkmsg.showwarning(
                        resource.settings.title,
                        f"The filter '{filter_element.name}' depends on the workspace "
                        f"element '{workspace_element}', but there is no element with "
                        "that name. Please create it in the workspace file.\n\n"
                        "The corresponding filter will be disabled for now.",
                    )
                    filter_element._enabled.set(False)

    @property
    def input_project(self) -> Combobox:
        """Returns the project combobox."""
        return self._combo_project

    @property
    def checkbox_bundle_data(self) -> Checkbutton:
        return self._chkbtn_bundle_data

    @property
    def checkbox_bundle_zip(self) -> Checkbutton:
        return self._chkbtn_bundle_zip

    @property
    def checkbox_bundle_by_prop(self) -> Checkbutton:
        return self._chkbtn_bundle_by_prop

    @property
    def input_bundle_by_prop_txt(self) -> Combobox:
        return self._combo_bundle_by_prop

    @property
    def input_bom_export_path(self) -> Entry:
        return self._entry_bom_export_path

    @property
    def button_bom_export_path(self) -> Button:
        return self._btn_browse_bom_export_path

    @property
    def input_documentation_export_path(self) -> Entry:
        return self._entry_docu_export_path

    @property
    def button_documentation_export_path(self) -> Button:
        return self._btn_browse_docu_export_path

    @property
    def label_docket_path(self) -> Label:
        return self._lbl_docket_export_path

    @property
    def input_docket_export_path(self) -> Entry:
        return self._entry_docket_export_path

    @property
    def button_docket_export_path(self) -> Button:
        return self._btn_browse_docket_export_path

    @property
    def label_drawing_path(self) -> Label:
        return self._lbl_drawing_export_path

    @property
    def input_drawing_export_path(self) -> Entry:
        return self._entry_drawing_export_path

    @property
    def button_drawing_export_path(self) -> Button:
        return self._btn_browse_drawing_export_path

    @property
    def label_stp_path(self) -> Label:
        return self._lbl_stp_export_path

    @property
    def input_stp_export_path(self) -> Entry:
        return self._entry_stp_export_path

    @property
    def button_stp_export_path(self) -> Button:
        return self._btn_browse_stp_export_path

    @property
    def label_stl_path(self) -> Label:
        return self._lbl_stl_export_path

    @property
    def input_stl_export_path(self) -> Entry:
        return self._entry_stl_export_path

    @property
    def button_stl_export_path(self) -> Button:
        return self._btn_browse_stl_export_path

    @property
    def label_jpg_path(self) -> Label:
        return self._lbl_jpg_export_path

    @property
    def input_jpg_export_path(self) -> Entry:
        return self._entry_jpg_export_path

    @property
    def button_jpg_export_path(self) -> Button:
        return self._btn_browse_jpg_export_path

    @property
    def label_bundle_path(self) -> Label:
        return self._lbl_bundle_export_path

    @property
    def input_bundle_export_path(self) -> Entry:
        return self._entry_bundle_export_path

    @property
    def button_bundle_export_path(self) -> Button:
        return self._btn_browse_bundle_export_path

    @property
    def checkbox_export_docket(self) -> Checkbutton:
        return self._chkbtn_export_docket

    @property
    def checkbox_export_documentation(self) -> Checkbutton:
        return self._chkbtn_export_documentation

    @property
    def checkbox_export_drawing(self) -> Checkbutton:
        return self._chkbtn_export_drawing

    @property
    def checkbox_export_stp(self) -> Checkbutton:
        return self._chkbtn_export_stp

    @property
    def checkbox_export_stl(self) -> Checkbutton:
        return self._chkbtn_export_stl

    @property
    def checkbox_export_jpg(self) -> Checkbutton:
        return self._chkbtn_export_jpg

    @property
    def checkbox_ignore_prefixed(self) -> Checkbutton:
        return self._chkbtn_ignore_prefixed

    @property
    def checkbox_ignore_source_unknown(self) -> Checkbutton:
        return self._chkbtn_ignore_unknown

    @property
    def input_ignore_prefixed_txt(self) -> Entry:
        return self._entry_ignore_prefix_txt

    @property
    def progress_bar(self) -> Progressbar:
        return self._progress_bar

    @property
    def tree_report_failed_items(self) -> Treeview:
        return self._tree_report_failed_items

    @property
    def tree_report_failed_props(self) -> Treeview:
        return self._tree_report_failed_props

    @property
    def text_description(self) -> Text:
        return self._text_description

    @property
    def text_log(self) -> Text:
        return self._text_log

    @property
    def button_export(self) -> Button:
        """Returns the export button."""
        return self._btn_export

    @property
    def button_open_document(self) -> Button:
        """Returns the open document button."""
        return self._btn_open_document

    @property
    def button_open_parent(self) -> Button:
        """Returns the open parent button."""
        return self._btn_open_parent

    @property
    def button_close_document(self) -> Button:
        """Returns the close document button."""
        return self._btn_close_document

    @property
    def button_exit(self) -> Button:
        """Returns the exit button."""
        return self._btn_exit

    @property
    def button_close_report(self) -> Button:
        """Returns the close report button."""
        return self._btn_close_report
