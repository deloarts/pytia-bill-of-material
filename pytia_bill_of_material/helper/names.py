"""
    Helper for names.
"""

from const import KEEP
from models.bom import BOMAssemblyItem
from pytia_ui_tools.handlers.workspace_handler import Workspace
from resources import resource


def get_bom_export_name(workspace: Workspace, project: str, machine: str) -> str:
    """
    Returns the name for the final excel bill of material file.
    The name set in the workspace config file will always be preferred to the name set in the
    settings.json file.

    The final file name will look like this:
    `PROJECT_NUMBER MACHINE_NUMBER BOM_NAME`

    The project number is omitted, if the number selection is set to KEEP.

    Args:
        workspace (Workspace): The workspace config.
        project (str): The project number for the final file.
        machine (str): The machine number for the final file.

    Returns:
        str: The file name without extension.
    """
    name = (
        workspace.elements.bom_name
        if workspace.elements.bom_name
        else resource.settings.files.bom_export,
    )[0]
    initial_file = f"{machine} {name}"

    if project != KEEP:
        initial_file = f"{project} {initial_file}"

    if ".xlsx" not in initial_file:
        initial_file += ".xlsx"

    return initial_file


def get_data_export_name(bom_item: BOMAssemblyItem) -> str:
    """
    Returns the name for generated data to export (docket, step, stl, ...).
    The export name will look like this:
    `PROJECT_NUMBER MACHINE_NUMBER PARTNUMBER REVISION`

    The revision will be prefixed with `Rev`.

    Args:
        bom_item (BOMAssemblyItem): The BOM object.

    Returns:
        str: The file name without extension.
    """
    # TODO: Make the export filename configurable in the settings.json
    return (
        f"{bom_item.properties[resource.bom.required_header_items.project]} "
        f"{bom_item.properties[resource.bom.required_header_items.machine]} "
        f"{bom_item.properties[resource.bom.required_header_items.partnumber]} "
        f"Rev{bom_item.properties[resource.bom.required_header_items.revision]}"
    )