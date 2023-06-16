"""
    Tooltips submodule for the app.
"""

from app.main.layout import Layout
from const import KEEP
from pytia_ui_tools.handlers.workspace_handler import Workspace
from pytia_ui_tools.widgets.tooltips import ToolTip
from resources import resource
from templates import templates


class ToolTips:
    """
    The ToolTips class. Responsible for initializing all tooltips for the main windows widgets.
    """

    def __init__(self, layout: Layout, workspace: Workspace) -> None:
        """
        Inits the ToolTips class.

        Args:
            layout (Layout): The layout of the main window.
            workspace (Workspace): The workspace instance.
            variables (Variables): The variables of the main window.
        """

        # region PROJECT NUMBER
        project_tooltip = (
            f"If set to {KEEP!r} the project number of each item in the bill of material and each "
            "docket will be used from the part or product properties. Otherwise the project number "
            "in the bill of material and each docket will be overwritten with the value from "
            "this input field."
        )
        if (
            resource.settings.restrictions.strict_project
            and workspace.elements.projects
        ):
            project_tooltip += (
                "\n\nThe rule for project numbers is set to 'strict'.\n\n"
                "You can only use project numbers that are set in the workspace file."
            )
        elif (
            resource.settings.restrictions.strict_project
            and workspace.available
            and not workspace.elements.projects
        ):
            project_tooltip += (
                "\n\nThe rule for project numbers is set to 'strict'.\n\n"
                "Warning: There are no project numbers set in the workspace file, you are "
                "allowed to use any project number of your choice. But it is recommended to "
                "setup the workspace file correctly."
            )
        elif resource.settings.restrictions.strict_project and not workspace.available:
            project_tooltip += (
                "\n\nThe rule for project numbers is set to 'strict'.\n\n"
                "Warning: No workspace file found. You are allowed to use any project number "
                "but you should consider setting up the workspace file correctly."
            )

        ToolTip(widget=layout.input_project, text=project_tooltip)
        # endregion

        # region PATHS
        bom_path_tooltip = (
            "Defines the path (folder and filename) of the bill of material Excel file. "
            "An existing file will be overwritten."
        )
        if (
            workspace.elements.bom_folder is not None
            and workspace.elements.bom_name is not None
        ):
            bom_path_tooltip += (
                "\n\nThe path has been pre-selected from the workspace file."
            )
        ToolTip(widget=layout.input_bom_export_path, text=bom_path_tooltip)
        ToolTip(
            widget=layout.button_bom_export_path,
            text=("Select the bill of material Excel file path."),
        )

        docket_path_tooltip = (
            "Defines the export folder of the generated docket files. "
            "Existing files are going to be overwritten."
        )
        if templates.docket_path is None:
            docket_path_tooltip += (
                "\n\nDisabled because no docket template is available."
            )
        elif workspace.elements.docket_folder is not None:
            docket_path_tooltip += (
                "\n\nThe path has been pre-selected from the workspace file."
            )
        ToolTip(widget=layout.input_docket_export_path, text=docket_path_tooltip)
        ToolTip(
            widget=layout.button_docket_export_path,
            text=("Select the folder into which all docket files will be exported."),
        )

        drawing_path_tooltip = (
            "Defines the export folder of the drawing files (pdf and dxf). "
            "Existing files are going to be overwritten."
        )
        if workspace.elements.drawing_folder is not None:
            drawing_path_tooltip += (
                "\n\nThe path has been pre-selected from the workspace file."
            )
        ToolTip(widget=layout.input_drawing_export_path, text=drawing_path_tooltip)
        ToolTip(
            widget=layout.button_drawing_export_path,
            text=("Select the folder into which all drawing files will be exported."),
        )

        stp_path_tooltip = (
            "Defines the export folder of the generated stp files. "
            "Existing files are going to be overwritten."
        )
        if workspace.elements.stp_folder is not None:
            stp_path_tooltip += (
                "\n\nThe path has been pre-selected from the workspace file."
            )
        ToolTip(widget=layout.input_stp_export_path, text=stp_path_tooltip)
        ToolTip(
            widget=layout.button_stp_export_path,
            text=("Select the folder into which all step files will be exported."),
        )

        stl_path_tooltip = (
            "Defines the export folder of the generated stl files. "
            "Existing files are going to be overwritten."
        )
        if workspace.elements.stl_folder is not None:
            stl_path_tooltip += (
                "\n\nThe path has been pre-selected from the workspace file."
            )
        ToolTip(widget=layout.input_stl_export_path, text=stl_path_tooltip)
        ToolTip(
            widget=layout.button_stl_export_path,
            text=("Select the folder into which all stl files will be exported."),
        )

        jpg_path_tooltip = (
            "Defines the export folder of the generated jpg files. "
            "Existing files are going to be overwritten."
        )
        if workspace.elements.png_folder is not None:
            jpg_path_tooltip += (
                "\n\nThe path has been pre-selected from the workspace file."
            )
        ToolTip(widget=layout.input_jpg_export_path, text=jpg_path_tooltip)
        ToolTip(
            widget=layout.button_jpg_export_path,
            text=("Select the folder into which all jpg files will be exported."),
        )
        # endregion

        # region EXPORT
        ToolTip(
            widget=layout.checkbox_export_docket,
            text=(
                "Generates a pdf docket for each item in the summary of the exported bill of "
                "material. Only exports items which are of source 'made'.\n\n"
                "This requires a valid path. Existing files at the target location will be "
                "overwritten."
            ),
        )

        export_drawing_tooltip = (
            "Saves the drawing as pdf and dxf file for each item in the summary of the "
            "exported bill of material.\n\n"
            "Only exports drawings that are linked to the document. The link will be set if "
            "you used the PYTIA Title Block Editor App on the drawing file.\n\n"
            "This requires a valid path. Existing files at the target location will be "
            "overwritten."
        )
        if resource.settings.export.lock_drawing_views:
            export_drawing_tooltip += "\n\nLocks all drawing views after the export to lock the version of the file."
        ToolTip(
            widget=layout.checkbox_export_drawing,
            text=export_drawing_tooltip,
        )
        ToolTip(
            widget=layout.checkbox_export_stp,
            text=(
                "Saves the 3d data as step-file for each item in the summary of the exported bill "
                "of material. Only exports items which are of source 'made'.\n\n"
                "This requires a valid path. Existing files at the target location will be "
                "overwritten."
            ),
        )
        ToolTip(
            widget=layout.checkbox_export_stl,
            text=(
                "Saves the 3d data as stl-file for each item in the summary of the exported bill "
                "of material. Only exports items which are of source 'made'.\n\n"
                "This requires a valid path. Existing files at the target location will be "
                "overwritten."
            ),
        )
        ToolTip(
            widget=layout.checkbox_export_jpg,
            text=(
                "Saves jpg images for each item in the summary of the exported bill "
                "of material. Only exports items which are of source 'made'.\n\n"
                "This requires a valid path. Existing files at the target location will be "
                "overwritten."
            ),
        )
        # endregion

        # region REPORT
        ToolTip(
            widget=layout.button_open_document,
            text=("Opens the document from the 'failed items' selection."),
        )
        ToolTip(
            widget=layout.button_open_parent,
            text=("Opens the parent document from the 'failed items' selection."),
        )
        ToolTip(
            widget=layout.button_close_document,
            text=(
                "Closes the currently open document and removes it from the 'failed items' "
                "selection.\n\nYou can also just close the current document in CATIA and the "
                "item will be removed from the 'failed items' list automatically."
            ),
        )
        # endregion
