"""
    Resource utilities.

    Important: Do not import third party modules here. This module
    must work on its own without any other dependencies!
"""

import os
import re
import sys
from tkinter import messagebox as tkmsg


def expand_env_vars(value: str) -> str:
    """
    Expands windows environment variables.
    E.g.: Expands %ONEDRIVE%/foo/bar to "C:/Users/.../OneDrive/foo/bar

    The variable to replace must be between two percentage symbols.

    Terminates the app if the given value has a variable, that
    cannot be found in the system variables.
    """
    output = value
    filter_result = re.findall(r"\%(.*?)\%", value)
    for key in filter_result:
        if key in os.environ:
            output = value.replace(f"%{key}%", os.environ[key])  # type: ignore
        else:
            tkmsg.showerror(
                title="Environment Variables",
                message=(
                    f"The environment variable {key!r} is not set on your machine. "
                    "Depending on your system it may be required to setup the "
                    "environment variable in capitals only.\n\n"
                    "Please contact your system administrator."
                ),
            )
            sys.exit()
    return output
