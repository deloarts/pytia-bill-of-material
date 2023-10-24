"""
    Submodule for system related functions.
"""

import os
import subprocess
from pathlib import Path

from const import EXPLORER
from psutil import (
    process_iter,  # Dependency of pytia, no need to add to the dependencies.json
)


def application_is_running(exe: str) -> bool:
    """
    Returns wether the app with the given name is running or not.

    Args:
        exe (str): The name of the app.

    Returns:
        bool: The state of the app. True if running, False otherwise.
    """
    return bool(exe in (p.name() for p in process_iter()))


def explorer(path: Path) -> None:
    """Opens the file explorer at the given path."""
    if os.path.isdir(path):
        subprocess.run([EXPLORER, path])
    elif os.path.isfile(path):
        subprocess.run([EXPLORER, "/select,", path])
