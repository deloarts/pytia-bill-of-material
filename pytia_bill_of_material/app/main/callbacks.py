"""
    The callbacks submodule for the main window.
"""

import os
from pathlib import Path
from pathlib import WindowsPath
from tkinter import DISABLED
from tkinter import NORMAL
from tkinter import Tk
from tkinter import filedialog
from tkinter import messagebox as tkmsg

from app.main.frames import Frames
from app.main.layout import Layout
from app.main.ui_setter import UISetter
from app.main.vars import Variables
from const import Status
from helper.callbacks import CallbackCommons
from helper.documents import ReportDocument
from helper.lazy_loaders import LazyDocumentHelper
from helper.names import get_bom_export_name
from pytia.log import log
from pytia_ui_tools.handlers.workspace_handler import Workspace
from pytia_ui_tools.helper.values import add_current_value_to_combobox_list
from resources import resource
from worker.main_task import MainTask


class Callbacks:
    """The callbacks class for the main window."""

    # TODO: Refactor into smaller bits.

    def __init__(
        self,
        root: Tk,
        variables: Variables,
        lazy_document_helper: LazyDocumentHelper,
        layout: Layout,
        workspace: Workspace,
        ui_setter: UISetter,
        frames: Frames,
    ) -> None:
        """
        Initializes the callbacks class.

        Args:
            root (Tk): The main window of the app.
            variables (Variables): The variables of the main window.
            lazy_document_helper (LazyDocumentHelper): The lazy document helper object.
            layout (Layout): The layout of the main window.
            workspace (Workspace): The workspace instance.
            ui_setter (UISetter): The ui setter instance of the main window.
        """
        self.root = root
        self.vars = variables
        self.doc_helper = lazy_document_helper
        self.layout = layout
        self.workspace = workspace
        self.set_ui = ui_setter
        self.frames = frames

        self.commons = CallbackCommons(layout=layout)
        self.report_doc = ReportDocument(root=root, commons=self.commons, layout=layout)

        # The treeview widget 'failed items' selection returns path variables.
        # Those are stored here. Maybe they should be moved to the variables class.
        self.report_selected_doc_path: Path | None
        self.report_selected_doc_parent_path: Path

        self._bind_button_callbacks()
        self._bind_checkbox_callbacks()
        self._bind_tree_callbacks()
        self._bind_widget_callbacks()
        log.info("Callbacks initialized.")

    def _bind_widget_callbacks(self) -> None:
        """Binds all callbacks to the main windows widgets."""
        if not (resource.settings.restrictions.strict_project and self.workspace.elements.projects):
            self.layout.input_project.bind(
                "<FocusOut>",
                lambda _: add_current_value_to_combobox_list(self.layout.input_project),
            )

    def _bind_button_callbacks(self) -> None:
        """Binds all callbacks to the main windows buttons."""
        self.layout.button_export.configure(command=self.on_btn_export)
        self.layout.button_exit.configure(command=self.on_btn_exit)
        self.layout.button_close_report.configure(command=self.on_btn_close_report)
        self.layout.button_open_document.configure(command=self.on_btn_open_document)
        self.layout.button_open_parent.configure(command=self.on_btn_open_parent)
        self.layout.button_close_document.configure(command=self.on_btn_close_document)

        self.layout.button_bom_export_path.configure(command=self.on_btn_bom_export_path)
        self.layout.button_docket_export_path.configure(command=self.on_btn_docket_export_path)
        self.layout.button_documentation_export_path.configure(command=self.on_btn_docu_export_path)
        self.layout.button_drawing_export_path.configure(command=self.on_btn_drawing_export_path)
        self.layout.button_stp_export_path.configure(command=self.on_btn_stp_export_path)
        self.layout.button_stl_export_path.configure(command=self.on_btn_stl_export_path)
        self.layout.button_jpg_export_path.configure(command=self.on_btn_jpg_export_path)
        self.layout.button_bundle_export_path.configure(command=self.on_btn_bundle_export_path)

    def _bind_checkbox_callbacks(self) -> None:
        """Bind checkbox callbacks."""
        self.layout.checkbox_export_docket.configure(command=self.on_chkbox_export_docket)
        self.layout.checkbox_export_drawing.configure(command=self.on_chkbox_export_drawing)
        self.layout.checkbox_export_stp.configure(command=self.on_chkbox_export_stp)
        self.layout.checkbox_export_stl.configure(command=self.on_chkbox_export_stl)

    def _bind_tree_callbacks(self) -> None:
        """Binds all callbacks to the main windows tree views."""
        self.layout.tree_report_failed_items.bind("<ButtonRelease-1>", self.on_tree_failed_items_button_1)
        self.layout.tree_report_failed_items.bind("<ButtonRelease-3>", self.on_tree_failed_items_button_3)
        self.layout.tree_report_failed_props.bind("<ButtonRelease-1>", self.on_tree_failed_props_button_1)

    def on_btn_export(self) -> None:
        """
        Event handler for the Export button. Starts the main task: The export.
        """
        log.info("Callback for button 'Export'.")
        self.set_ui.working()
        main_task = MainTask(
            main_ui=self.root,
            layout=self.layout,
            ui_setter=self.set_ui,
            doc_helper=self.doc_helper,
            variables=self.vars,
            frames=self.frames,
            workspace=self.workspace,
        )
        self.root.after(100, main_task.run)

    def on_btn_exit(self) -> None:
        """Callback function for the exit button. Closes the app."""
        log.info("Callback for button 'Exit'.")

        if resource.settings.restrictions.enable_information:
            for msg in resource.get_info_msg_by_counter():
                tkmsg.showinfo(title=resource.settings.title, message=f"Did you know:\n\n{msg}")

        self.root.withdraw()
        self.root.destroy()

    def on_btn_close_report(self) -> None:
        """
        Event handler for the close report button. Toggles the show_report variable to
        False, which results in hiding the report frame.
        """
        log.info("Callback for button 'Close Report'.")
        self.vars.show_report.set(False)  # This variable has a trace, see traces.py

    def on_btn_open_document(self) -> None:
        """
        Event handler for the open document button. Opens the document from the failed items
        treeview selection.
        """
        log.info("Callback for button 'Open Document'.")
        if self.report_selected_doc_path is not None:
            self.report_doc.open_wait_for_close(path=self.report_selected_doc_path)

    def on_btn_open_parent(self) -> None:
        """
        Event handler for the open parent button. Opens the parent document from the failed items
        treeview selection.
        """
        log.info("Callback for button 'Open Parent'.")
        self.report_doc.open_wait_for_close(path=self.report_selected_doc_parent_path)

    def on_btn_close_document(self) -> None:
        """
        Event handler for the close document button. Closes the current document.
        """
        log.info("Callback for button 'Close Document'.")
        self.report_doc.close()

    def on_btn_bom_export_path(self) -> None:
        """
        Event handler for the browse bom export path button. Asks the user to select a xlsx file,
        to which to export the final bill of material.
        """
        log.info("Callback for button 'Browse bom export path'.")

        initial_dir = Path(self.vars.bom_export_path.get()).parent
        if (
            not initial_dir.is_absolute()
            and self.workspace.workspace_folder
            and self.workspace.workspace_folder.exists()
        ):
            initial_dir = self.workspace.workspace_folder

        if path := WindowsPath(
            filedialog.asksaveasfilename(
                filetypes=[("EXCEL Worksheet", "*.xlsx")],
                defaultextension=".xlsx",
                initialdir=initial_dir,
                initialfile=get_bom_export_name(
                    workspace=self.workspace,
                    project=self.vars.project.get(),
                    product=self.vars.product.get(),
                ),
                title=resource.settings.title,
            )
        ):
            self.vars.bom_export_path.set(str(path))

    def on_btn_docket_export_path(self) -> None:
        """
        Event handler for the browse docket export path button. Asks the user to select a folder,
        into which to export the docket files.
        """
        log.info("Callback for button 'Browse docket export path'.")

        initial_dir = Path(self.vars.docket_export_path.get())
        if (
            not initial_dir.is_absolute()
            and self.workspace.workspace_folder
            and self.workspace.workspace_folder.exists()
        ):
            initial_dir = self.workspace.workspace_folder

        if path := WindowsPath(
            filedialog.askdirectory(
                initialdir=initial_dir,
                title=resource.settings.title,
            )
        ):
            self.vars.docket_export_path.set(str(path))

    def on_btn_docu_export_path(self) -> None:
        """
        Event handler for the browse documentation export path button. Asks the user
        to select a folder, into which to export the docket files.
        """
        log.info("Callback for button 'Browse documentation export path'.")

        initial_dir = Path(self.vars.documentation_export_path.get())
        if (
            not initial_dir.is_absolute()
            and self.workspace.workspace_folder
            and self.workspace.workspace_folder.exists()
        ):
            initial_dir = self.workspace.workspace_folder

        if path := WindowsPath(
            filedialog.askdirectory(
                initialdir=initial_dir,
                title=resource.settings.title,
            )
        ):
            self.vars.documentation_export_path.set(str(path))

    def on_btn_drawing_export_path(self) -> None:
        """
        Event handler for the browse drawing export path button. Asks the user to select a folder,
        into which to export the pdf and dxf files.
        """
        log.info("Callback for button 'Browse Drawing export path'.")

        initial_dir = Path(self.vars.drawing_export_path.get())
        if (
            not initial_dir.is_absolute()
            and self.workspace.workspace_folder
            and self.workspace.workspace_folder.exists()
        ):
            initial_dir = self.workspace.workspace_folder

        if path := WindowsPath(
            filedialog.askdirectory(
                initialdir=initial_dir,
                title=resource.settings.title,
            )
        ):
            self.vars.drawing_export_path.set(str(path))

    def on_btn_stp_export_path(self) -> None:
        """
        Event handler for the browse stp export path button. Asks the user to select a folder,
        into which to export the stp files.
        """
        log.info("Callback for button 'Browse STP export path'.")

        initial_dir = Path(self.vars.stp_export_path.get())
        if (
            not initial_dir.is_absolute()
            and self.workspace.workspace_folder
            and self.workspace.workspace_folder.exists()
        ):
            initial_dir = self.workspace.workspace_folder

        if path := WindowsPath(
            filedialog.askdirectory(
                initialdir=initial_dir,
                title=resource.settings.title,
            )
        ):
            self.vars.stp_export_path.set(str(path))

    def on_btn_stl_export_path(self) -> None:
        """
        Event handler for the browse stl export path button. Asks the user to select a folder,
        into which to export the stl files.
        """
        log.info("Callback for button 'Browse STL export path'.")

        initial_dir = Path(self.vars.stl_export_path.get())
        if (
            not initial_dir.is_absolute()
            and self.workspace.workspace_folder
            and self.workspace.workspace_folder.exists()
        ):
            initial_dir = self.workspace.workspace_folder

        if path := WindowsPath(
            filedialog.askdirectory(
                initialdir=initial_dir,
                title=resource.settings.title,
            )
        ):
            self.vars.stl_export_path.set(str(path))

    def on_btn_jpg_export_path(self) -> None:
        """
        Event handler for the browse jpg export path button. Asks the user to select a folder,
        into which to export the jpg files.
        """
        log.info("Callback for button 'Browse JPG export path'.")

        initial_dir = Path(self.vars.jpg_export_path.get())
        if (
            not initial_dir.is_absolute()
            and self.workspace.workspace_folder
            and self.workspace.workspace_folder.exists()
        ):
            initial_dir = self.workspace.workspace_folder

        if path := WindowsPath(
            filedialog.askdirectory(
                initialdir=initial_dir,
                title=resource.settings.title,
            )
        ):
            self.vars.jpg_export_path.set(str(path))

    def on_btn_bundle_export_path(self) -> None:
        """
        Event handler for the browse bundle export path button. Asks the user to select a folder,
        into which to export the files.
        """
        log.info("Callback for button 'Browse Bundle export path'.")

        initial_dir = Path(self.vars.bundle_export_path.get())
        if (
            not initial_dir.is_absolute()
            and self.workspace.workspace_folder
            and self.workspace.workspace_folder.exists()
        ):
            initial_dir = self.workspace.workspace_folder

        if path := WindowsPath(
            filedialog.askdirectory(
                initialdir=initial_dir,
                title=resource.settings.title,
            )
        ):
            self.vars.bundle_export_path.set(str(path))

    def on_chkbox_export_docket(self) -> None:
        """
        Event handler for the checkbox 'export docket'. Does nothing.
        """
        log.info(f"Callback for checkbox 'Export docket': {self.vars.export_docket.get()}")

    def on_chkbox_export_drawing(self) -> None:
        """
        Event handler for the checkbox 'export drawing'. Does nothing.
        """
        log.info(f"Callback for checkbox 'Export Drawing': {self.vars.export_drawing.get()}")

    def on_chkbox_export_stp(self) -> None:
        """
        Event handler for the checkbox 'export stp'. Does nothing.
        """
        log.info(f"Callback for checkbox 'Export STP': {self.vars.export_stp.get()}")

    def on_chkbox_export_stl(self) -> None:
        """
        Event handler for the checkbox 'export stl'. Does nothing.
        """
        log.info(f"Callback for checkbox 'Export STL': {self.vars.export_stl.get()}")

    def on_chkbox_export_jpg(self) -> None:
        """
        Event handler for the checkbox 'export jpg'. Does nothing.
        """
        log.info(f"Callback for checkbox 'Export JPG': {self.vars.export_jpg.get()}")

    def on_tree_failed_items_button_1(self, *_) -> None:
        """
        Event handler for the treeview widget 'failed items': Left mouse button.
        Handles the user selection of the failed item. Enables the open document buttons and
        adds the failed properties from the report to the 'failed props' treeview widget.
        """
        self.layout.tree_report_failed_props.delete(*self.layout.tree_report_failed_props.get_children())
        self.layout.text_description.delete("1.0", "end")

        selection = self.layout.tree_report_failed_items.selection()

        for selection_item in selection:
            partnumber = self.layout.tree_report_failed_items.item(selection_item, "values")[0]
            parent_partnumber = self.layout.tree_report_failed_items.item(selection_item, "values")[1]

            if partnumber and parent_partnumber:
                for item in self.vars.report.items:
                    if item.partnumber == partnumber and item.parent_partnumber == parent_partnumber:
                        self.report_selected_doc_path = item.path
                        self.report_selected_doc_parent_path = item.parent_path
                        for detail in item.details:
                            if item.details[detail] == Status.FAILED:
                                if filter_element := resource.get_filter_element_by_name(detail):
                                    self.layout.tree_report_failed_props.insert(
                                        "",
                                        "end",
                                        values=(
                                            filter_element.name,
                                            filter_element.property_name,
                                        ),
                                    )
                                else:
                                    self.layout.tree_report_failed_props.insert("", "end", values=(detail, "-"))

                if os.path.isfile(self.report_selected_doc_parent_path):
                    self.layout.button_open_parent.configure(state=NORMAL)

                if self.report_selected_doc_path is None:
                    self.layout.text_description.configure(state=NORMAL)
                    self.layout.text_description.delete("1.0", "end")
                    self.layout.text_description.insert("end", "Path for element not found.")
                    self.layout.text_description.configure(state=DISABLED)
                elif os.path.isfile(self.report_selected_doc_path):
                    self.layout.button_open_document.configure(state=NORMAL)
            else:
                self.layout.button_open_document.configure(state=DISABLED)
                self.layout.button_open_parent.configure(state=DISABLED)

    def on_tree_failed_items_button_3(self, *_) -> None:
        """
        Event handler for the treeview 'failed items': Right mouse button: Removes the selection.
        """
        self.commons.remove_selection_from_failed_items()

    def on_tree_failed_props_button_1(self, *_) -> None:
        """
        Event handler fot the treeview 'failed props': Left mouse button: Shows the description of
        the failed property.
        """
        self.layout.text_description.configure(state=NORMAL)
        self.layout.text_description.delete("1.0", "end")
        selection = self.layout.tree_report_failed_props.selection()
        for selection_item in selection:
            if filter_element_name := self.layout.tree_report_failed_props.item(selection_item, "values")[0]:
                if filter_element := resource.get_filter_element_by_name(filter_element_name):
                    self.layout.text_description.insert(
                        "end",
                        f"{filter_element.description}\n\n"
                        f"This results from an error in the document property '{filter_element.property_name}'.",
                    )
                    return
                else:
                    self.layout.text_description.insert("end", "No description available.")
        self.layout.text_description.configure(state=DISABLED)
