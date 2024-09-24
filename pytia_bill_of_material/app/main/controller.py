"""
    Controller submodule for the main window's flow.
"""

import os
from pathlib import Path
from tkinter import Tk
from tkinter import messagebox as tkmsg

from app.main.layout import Layout
from app.main.ui_setter import UISetter
from app.main.vars import Variables
from const import KEEP
from const import LOGON
from helper.folders import set_default_folder_and_checkbox_from_workspace
from helper.lazy_loaders import LazyDocumentHelper
from helper.names import get_bom_export_name
from pytia.exceptions import PytiaPropertyNotFoundError
from pytia_ui_tools.handlers.workspace_handler import Workspace
from resources import resource
from templates import templates


class Controller:
    """The Controller class for the main window's flow."""

    def __init__(
        self,
        root: Tk,
        doc_helper: LazyDocumentHelper,
        layout: Layout,
        vars: Variables,
        ui_setter: UISetter,
        workspace: Workspace,
    ) -> None:
        """
        Inits the Controller class.

        Args:
            root (Tk): The main window object.
            doc_helper (LazyDocumentHelper): The document helper object.
            layout (Layout): The layout of the main window.
            vars (Variables): The variables of the main window.
            ui_setter (UISetter): The state setter for the main window.
            workspace (Workspace): The workspace object.
        """
        self.root = root
        self.doc_helper = doc_helper
        self.layout = layout
        self.vars = vars
        self.set_ui = ui_setter
        self.workspace = workspace

        self.activate_ui = True

    def run_all_controllers(self):
        """Runs all controllers: This is the setup routine for the app."""
        self._permission_controller()
        self._property_controller()
        self._default_values_controller()

        if self.activate_ui:
            self.set_ui.normal()
        else:
            self.set_ui.disabled()

    def _permission_controller(self) -> None:
        """
        Runs the permission controller. Handles permissions set in the settings.json and in the
        workspace file.
        """
        # Check if the workspace is active
        if not self.workspace.elements.active:
            self.activate_ui = False
            tkmsg.showinfo(
                title=resource.settings.title,
                message=(
                    "This workspace is disabled. You cannot export the bill of material of this "
                    "document."
                ),
            )
            return

        # Check user config permission.
        if (
            not resource.logon_exists()
            and not resource.settings.restrictions.allow_all_users
        ):
            self.activate_ui = False
            tkmsg.showinfo(
                title=resource.settings.title,
                message=(
                    "You are not allowed to export the bill of material: Your logon "
                    f"name ({LOGON}) doesn't exist in the user configuration."
                ),
            )
            return

        # Check workspace permission.
        if (
            self.workspace.elements.editors
            and LOGON not in self.workspace.elements.editors
            and not resource.settings.restrictions.allow_all_editors
        ):
            self.activate_ui = False
            tkmsg.showinfo(
                title=resource.settings.title,
                message=(
                    "You are not allowed to export the bill of material: Your logon "
                    f"name ({LOGON}) doesn't exist in the workspace configuration."
                ),
            )
            return

    def _property_controller(self) -> None:
        """Run the property controller. Handles the main product's properties."""
        # Set product property
        if (
            product_property := self.doc_helper.get_property(
                name=resource.props.product
            )
        ) is None:
            raise PytiaPropertyNotFoundError(
                f"Cannot find required property {resource.props.product!r} in the main product. "
                "Please run the Property Manager App first."
            )
        self.vars.product.set(product_property)

    def _default_values_controller(self) -> None:
        """
        Run the default values controller. Applies the settings from the workspace settings file.
        """
        # Set project
        project_values = [KEEP]
        if self.workspace.elements.projects:
            project_values.extend(self.workspace.elements.projects)
        self.layout.input_project.configure(values=project_values)
        # self.vars.project.set(KEEP)

        # Set property combo box
        self.layout.input_bundle_by_prop_txt.configure(
            values=[k for k in resource.bom.header_items.summary_as_dict().keys()]
        )

        # Write default bom export path
        bom_folder: Path
        bom_name = get_bom_export_name(
            workspace=self.workspace,
            project=self.vars.project.get(),
            product=self.vars.product.get(),
        )
        if self.workspace.elements.bom_folder is not None:
            if os.path.isdir(self.workspace.elements.bom_folder):
                bom_folder = Path(self.workspace.elements.bom_folder)
                self.vars.bom_export_path.set(str(Path(bom_folder, bom_name)))

            elif self.workspace.workspace_folder is not None and os.path.isdir(
                _bom_folder := Path(
                    self.workspace.workspace_folder, self.workspace.elements.bom_folder
                )
            ):
                self.vars.bom_export_path.set(str(Path(_bom_folder, bom_name)))

        # Write default docket export path
        if templates.docket_path is not None:
            set_default_folder_and_checkbox_from_workspace(
                workspace_folder=self.workspace.workspace_folder,
                workspace_default_path=self.workspace.elements.docket_folder,
                export_path_variable=self.vars.docket_export_path,
                export_checkbox_variable=self.vars.export_docket,
            )

        if templates.documentation_path is not None:
            set_default_folder_and_checkbox_from_workspace(
                workspace_folder=self.workspace.workspace_folder,
                workspace_default_path=self.workspace.elements.documentation_folder,
                export_path_variable=self.vars.documentation_export_path,
                export_checkbox_variable=self.vars.export_documentation,
            )

        # Write default stp export path
        set_default_folder_and_checkbox_from_workspace(
            workspace_folder=self.workspace.workspace_folder,
            workspace_default_path=self.workspace.elements.drawing_folder,
            export_path_variable=self.vars.drawing_export_path,
            export_checkbox_variable=self.vars.export_drawing,
        )

        # Write default stp export path
        set_default_folder_and_checkbox_from_workspace(
            workspace_folder=self.workspace.workspace_folder,
            workspace_default_path=self.workspace.elements.stp_folder,
            export_path_variable=self.vars.stp_export_path,
            export_checkbox_variable=self.vars.export_stp,
        )

        # Write default stl export path
        set_default_folder_and_checkbox_from_workspace(
            workspace_folder=self.workspace.workspace_folder,
            workspace_default_path=self.workspace.elements.stl_folder,
            export_path_variable=self.vars.stl_export_path,
            export_checkbox_variable=self.vars.export_stl,
        )

        # Write default jpg export path
        set_default_folder_and_checkbox_from_workspace(
            workspace_folder=self.workspace.workspace_folder,
            workspace_default_path=self.workspace.elements.image_folder,
            export_path_variable=self.vars.jpg_export_path,
            export_checkbox_variable=self.vars.export_jpg,
        )
