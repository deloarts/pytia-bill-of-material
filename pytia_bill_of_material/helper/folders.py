"""
    Helper functions for working with folders.
"""

import os
from pathlib import Path
from tkinter import BooleanVar
from tkinter import StringVar


def set_default_folder_and_checkbox_from_workspace(
    workspace_folder: Path | None,
    workspace_default_path: str | None,
    export_path_variable: StringVar,
    export_checkbox_variable: BooleanVar,
) -> None:
    """
    Sets the path variable and the checkbox from the export settings accordingly to the
    values from the workspace.

    Doesn't do anything if no workspace is provided.

    Args:
        workspace_folder (Path | None): The folder in which the workspace file is stored.
        workspace_default_path (str | None): The default path for the export. Path can be absolute \
            or relative (root folder will be the workspace_folder).
        export_path_variable (StringVar): The path variable which holds the export path.
        export_checkbox_variable (BooleanVar): The checkbox which toggles wether to export data or \
            not.
    """
    if workspace_folder is not None and workspace_default_path is not None:
        if os.path.isdir(workspace_default_path):
            export_path_variable.set(str(Path(workspace_default_path).resolve()))
            export_checkbox_variable.set(True)

        elif os.path.isdir(
            _folder := Path(
                workspace_folder,
                workspace_default_path,
            ).resolve()
        ):
            export_path_variable.set(str(_folder))
            export_checkbox_variable.set(True)
