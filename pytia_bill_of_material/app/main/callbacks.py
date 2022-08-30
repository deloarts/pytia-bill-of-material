"""
    The callbacks submodule for the main window.
"""

import os
from pathlib import Path, WindowsPath
from tkinter import DISABLED, NORMAL, Tk, filedialog
from tkinter import messagebox as tkmsg

from app.main.layout import Layout
from app.main.ui_setter import UISetter
from app.main.vars import Variables
from const import Status
from helper.lazy_loaders import LazyDocumentHelper
from helper.names import get_bom_export_name
from pytia.framework import framework
from pytia.framework.in_interfaces.document import Document
from pytia.log import log
from pytia_ui_tools.handlers.workspace_handler import Workspace
from pytia_ui_tools.helper.values import add_current_value_to_combobox_list
from resources import resource
from worker.main_task import MainTask


class Commons:
    """Commons class for the callback class."""

    def __init__(self, layout: Layout) -> None:
        """
        Inits the Commons class. Requires the layout of the main window.

        Args:
            layout (Layout): The layout of the main window.
        """
        self.layout = layout

    def remove_selection_from_failed_items(self) -> None:
        """Removes the selection from the failed items widget."""
        try:
            selection = self.layout.tree_report_failed_items.selection()[0]
            self.layout.tree_report_failed_items.delete(selection)
            self.layout.tree_report_failed_props.delete(
                *self.layout.tree_report_failed_props.get_children()
            )
            self.layout.text_description.configure(state=NORMAL)
            self.layout.text_description.delete("1.0", "end")
            self.layout.text_description.configure(state=DISABLED)

            self.layout.button_open_document.configure(state=DISABLED)
            self.layout.button_open_parent.configure(state=DISABLED)
            self.layout.button_close_document.configure(state=DISABLED)
            self.layout.tree_report_failed_items.state(("!disabled",))
        except IndexError:
            pass


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
        self.commons = Commons(layout=layout)

        self.root = root
        self.vars = variables
        self.doc_helper = lazy_document_helper
        self.layout = layout
        self.workspace = workspace
        self.set_ui = ui_setter

        # The treeview widget 'failed items' selection returns path variables.
        # Those are stored here. Maybe they should be moved to the variables class.
        self.report_selected_doc_path: Path
        self.report_selected_doc_parent_path: Path

        self._bind_button_callbacks()
        self._bind_checkbox_callbacks()
        self._bind_tree_callbacks()
        self._bind_widget_callbacks()
        log.info("Callbacks initialized.")

    def _bind_widget_callbacks(self) -> None:
        """Binds all callbacks to the main windows widgets."""
        if not (
            resource.settings.restrictions.strict_project
            and self.workspace.elements.projects
        ):
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

        self.layout.button_bom_export_path.configure(
            command=self.on_btn_bom_export_path
        )
        self.layout.button_docket_export_path.configure(
            command=self.on_btn_docket_export_path
        )
        self.layout.button_stp_export_path.configure(
            command=self.on_btn_stp_export_path
        )
        self.layout.button_stl_export_path.configure(
            command=self.on_btn_stl_export_path
        )

    def _bind_checkbox_callbacks(self) -> None:
        """Bind checkbox callbacks."""
        self.layout.checkbox_export_docket.configure(
            command=self.on_chkbox_export_docket
        )
        self.layout.checkbox_export_stp.configure(command=self.on_chkbox_export_stp)
        self.layout.checkbox_export_stl.configure(command=self.on_chkbox_export_stl)

    def _bind_tree_callbacks(self) -> None:
        """Binds all callbacks to the main windows tree views."""
        self.layout.tree_report_failed_items.bind(
            "<ButtonRelease-1>", self.on_tree_failed_items_button_1
        )
        self.layout.tree_report_failed_items.bind(
            "<ButtonRelease-3>", self.on_tree_failed_items_button_3
        )
        self.layout.tree_report_failed_props.bind(
            "<ButtonRelease-1>", self.on_tree_failed_props_button_1
        )

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
        )
        self.root.after(100, main_task.run)

    def on_btn_exit(self) -> None:
        """Callback function for the exit button. Closes the app."""
        log.info("Callback for button 'Exit'.")

        if resource.settings.restrictions.enable_information:
            for msg in resource.get_info_msg_by_counter():
                tkmsg.showinfo(
                    title=resource.settings.title, message=f"Did you know:\n\n{msg}"
                )

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
        if self.report_selected_doc_path and os.path.isfile(
            self.report_selected_doc_path
        ):
            framework.catia.documents.open(self.report_selected_doc_path)
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
        else:
            tkmsg.showerror(
                title=resource.settings.title,
                message=(f"Cannot open document {self.report_selected_doc_path!r}."),
            )

    def on_btn_open_parent(self) -> None:
        """
        Event handler for the open parent button. Opens the parent document from the failed items
        treeview selection.
        """
        log.info("Callback for button 'Open Parent'.")
        if self.report_selected_doc_parent_path and os.path.isfile(
            self.report_selected_doc_parent_path
        ):
            framework.catia.documents.open(self.report_selected_doc_parent_path)
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
        else:
            tkmsg.showerror(
                title=resource.settings.title,
                message=(
                    f"Cannot open document {self.report_selected_doc_parent_path!r}."
                ),
            )

    def on_btn_close_document(self) -> None:
        """
        Event handler for the close document button. Closes the current document.
        """
        log.info("Callback for button 'Close Document'.")
        document = Document(framework.catia.active_document.com_object)
        document.save()
        document.close()
        self.commons.remove_selection_from_failed_items()

    def on_btn_bom_export_path(self) -> None:
        """
        Event handler for the browse bom export path button. Asks the user to select a xlsx file,
        to which to export the final bill of material.
        """
        if path := WindowsPath(
            filedialog.asksaveasfilename(
                filetypes=[("EXCEL Worksheet", "*.xlsx")],
                defaultextension=".xlsx",
                initialdir=Path(self.vars.bom_export_path.get()).parent,
                initialfile=get_bom_export_name(
                    workspace=self.workspace,
                    project=self.vars.project.get(),
                    machine=self.vars.machine.get(),
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
        if path := WindowsPath(
            filedialog.askdirectory(
                initialdir=self.vars.docket_export_path.get(),
                title=resource.settings.title,
            )
        ):
            self.vars.docket_export_path.set(str(path))

    def on_btn_stp_export_path(self) -> None:
        """
        Event handler for the browse stp export path button. Asks the user to select a folder,
        into which to export the stp files.
        """
        log.info("Callback for button 'Browse STP export path'.")
        if path := WindowsPath(
            filedialog.askdirectory(
                initialdir=self.vars.stp_export_path.get(),
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
        if path := WindowsPath(
            filedialog.askdirectory(
                initialdir=self.vars.stl_export_path.get(),
                title=resource.settings.title,
            )
        ):
            self.vars.stl_export_path.set(str(path))

    def on_chkbox_export_docket(self) -> None:
        """
        Event handler for the checkbox 'export docket'. Does nothing.
        """
        log.info(
            f"Callback for checkbox 'Export docket': {self.vars.export_docket.get()}"
        )

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

    def on_tree_failed_items_button_1(self, *_) -> None:
        """
        Event handler for the treeview widget 'failed items': Left mouse button.
        Handles the user selection of the failed item. Enables the open document buttons and
        adds the failed properties from the report to the 'failed props' treeview widget.
        """
        self.layout.tree_report_failed_props.delete(
            *self.layout.tree_report_failed_props.get_children()
        )

        selection = self.layout.tree_report_failed_items.selection()
        for selection_item in selection:
            if partnumber := self.layout.tree_report_failed_items.item(
                selection_item, "values"
            )[0]:
                for item in self.vars.report.items:
                    if item.partnumber == partnumber:
                        self.report_selected_doc_path = item.path
                        self.report_selected_doc_parent_path = item.parent_path
                        for detail in item.details:
                            if item.details[detail] == Status.FAILED:
                                self.layout.tree_report_failed_props.insert(
                                    "", "end", values=(detail,)
                                )
                if os.path.isfile(self.report_selected_doc_path):
                    self.layout.button_open_document.configure(state=NORMAL)
                if os.path.isfile(self.report_selected_doc_parent_path):
                    self.layout.button_open_parent.configure(state=NORMAL)
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
            if property_name := self.layout.tree_report_failed_props.item(
                selection_item, "values"
            )[0]:
                if filter_element := resource.get_filter_element_by_property_name(
                    property_name
                ):
                    self.layout.text_description.insert(
                        "end", filter_element.description
                    )
                    return
                else:
                    self.layout.text_description.insert(
                        "end", "No description available."
                    )
        self.layout.text_description.configure(state=DISABLED)
