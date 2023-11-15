"""
    Helper functions for working with files.
"""

from pathlib import Path
from tkinter import Tk
from tkinter import messagebox as tkmsg
from tkinter import simpledialog

from app.main.vars import Variables
from pytia.exceptions import PytiaFileNotFoundError
from resources import resource


def set_external_bom_file(root: Tk, vars: Variables) -> None:
    path = simpledialog.askstring(
        title=resource.settings.title,
        prompt=(
            "Enter the path of the external EXCEL document. "
            "Be sure that the Format is correct (use Tools/Set BOM Format)."
        ),
        parent=root,
    )

    if path is None:
        tkmsg.showerror(title=resource.settings.title, message="Input not valid.")
        return

    if not Path(path).is_file():
        tkmsg.showerror(
            title=resource.settings.title, message="The given input is not a file."
        )
        return

    if not ".xls" in path:
        tkmsg.showerror(
            title=resource.settings.title,
            message="The given file is no EXCEL document.",
        )
        return

    vars.external_bom_path.set(path)
    tkmsg.showinfo(
        title=resource.settings.title,
        message="The given file has been accepted.",
    )
