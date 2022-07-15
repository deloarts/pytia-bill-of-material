"""
    Installs/updates required dependencies.
    Some deps may not be available on PyPi or GitHub (or are private),
    therefor it's necessary to provide them locally.

    All required dependencies are specified in the dependencies.json
    resource file.

    .. warning::
        Do not import third party modules here.
        This module must work on its own without any other dependencies!
"""

import importlib.resources
import json
import os
import pathlib
import subprocess
import sys
import tkinter as tk
import tkinter.messagebox as tkmsg
from dataclasses import dataclass
from distutils.version import (
    LooseVersion,
)  # WARNING: Module will be removed in Python 3.12
from http.client import HTTPSConnection
from importlib import metadata
from socket import gaierror
from tkinter import ttk
from typing import Dict, List

from const import CNEXT, CONFIG_DEPS, VENV_PYTHON, VENV_PYTHONW, WEB_PIP
from resources import resource


@dataclass(slots=True, kw_only=True, frozen=True)
class PackageInfo:
    """
    Dataclass for package infos from the dependencies.json.

    .. warning::
        The content of the dependencies.json must match the list of dependencies specified in the
        pyproject.toml file at the key **tool.poetry.dependencies**
    """

    name: str
    version: str
    local: bool


class Dependencies:
    """Class for managing dependencies."""

    __slots__ = ("_required_packages", "_missing_packages", "_runs_in_venv")

    def __init__(self) -> None:
        self._required_packages = self._read_dependencies_file()
        self._missing_packages = self.get_missing_packages()
        self._runs_in_venv = (
            VENV_PYTHON in sys.executable or VENV_PYTHONW in sys.executable
        )

    @staticmethod
    def _read_dependencies_file() -> List[PackageInfo]:
        """
        Reads the deps json from the resources folder.

        Returns:
            List[PackageInfo]: The dependencies as a list.
        """
        with importlib.resources.open_binary("resources", CONFIG_DEPS) as f:
            return [PackageInfo(**i) for i in json.load(f)]

    @staticmethod
    def _pip_available() -> bool:
        """Returns wether pypi is available or not."""
        conn = HTTPSConnection(WEB_PIP, timeout=5)
        try:
            conn.request("HEAD", "/")
            return True
        except gaierror:
            return False
        finally:
            conn.close()

    def _remove_venv(self) -> None:
        pass

    def _get_pip_commands(self) -> Dict[str, str]:
        """Returns a dict of all package-names and install commands for installing with pip."""
        pip = {}
        err = []

        for package in self._missing_packages:
            if package.local:
                if os.path.isdir(resource.settings.paths.local_dependencies):
                    package_not_found = True
                    for wheel in pathlib.Path(
                        resource.settings.paths.local_dependencies
                    ).glob("*.whl"):
                        wheel_name = str(wheel)
                        if f"{package.name}-{package.version}" in wheel_name:
                            pip[package.name] = wheel_name
                            package_not_found = False
                    if package_not_found:
                        err.append(f"\n - {package.name} {package.version}")
                else:
                    tkmsg.showerror(
                        title=resource.settings.title,
                        message=(
                            f"The local dependencies folder "
                            f"({resource.settings.paths.local_dependencies}) "
                            f"cannot be accessed or doesn't exist."
                        ),
                    )
                    sys.exit()
            else:
                pip[package.name] = f'"{package.name}=={package.version}"'

        if err:
            tkmsg.showerror(
                title=resource.settings.title,
                message=(
                    f"Cannot install local dependencies: {''.join(err)}\n\n"
                    f"Python wheel not found in folder "
                    f"{resource.settings.paths.local_dependencies}\n\n"
                    f"Please notify your system administrator immediately."
                ),
            )
            sys.exit()

        return pip

    def get_missing_packages(self) -> List[PackageInfo]:
        """Returns a list of missing packages."""
        missing_packages = []
        for package in self._required_packages:
            try:
                dist_version = metadata.version(package.name)
                if LooseVersion(dist_version) < LooseVersion(package.version):
                    missing_packages.append(package)
            except metadata.PackageNotFoundError:
                missing_packages.append(package)
        return missing_packages

    def install_dependencies(self) -> None:
        """Installs missing dependencies."""
        if pip := self._get_pip_commands():
            if not self._runs_in_venv:
                result = tkmsg.askyesno(
                    title=resource.settings.title,
                    message=(
                        "The app is not running in its virtualenv environment. "
                        "This will install all dependencies global, which can lead to unexpected "
                        "behaviour.\n\nProceed with installing dependencies global?\n\n"
                        "Hint: To run the app in its environment use the launcher."
                    ),
                    icon="warning",
                )
                if not result:
                    sys.exit()

            if self._pip_available():
                # subprocess.call(
                #     f"start /wait python -m pip install {' '.join(pip)} --no-cache-dir",
                #     shell=True,
                # )
                installer = VisualInstaller()
                installer.install(pip)
                if missing_packages := self.get_missing_packages():
                    tkmsg.showerror(
                        title=resource.settings.title,
                        message=(
                            f"Installation of "
                            f"{', '.join(package.name for package in missing_packages)} failed.\n\n"
                            f"Please notify your system administrator immediately."
                        ),
                    )
                else:
                    tkmsg.showinfo(
                        title=resource.settings.title,
                        message=(
                            "Successfully updated the app.\n\n"
                            "The app will start automatically, once all changes have been applied. "
                            "This may take a while.\n\nClick OK to continue."
                        ),
                    )
                    subprocess.Popen(  # pylint: disable=R1732
                        [
                            f"{resource.settings.paths.catia}\\{CNEXT}",
                            "-batch",
                            "-macro",
                            f"{resource.settings.paths.release}\\"
                            f"{resource.settings.files.launcher}",
                        ]
                    )
            else:
                tkmsg.showerror(
                    title=resource.settings.title,
                    message="Cannot install required dependencies: No internet connection.",
                )
            sys.exit()


class VisualInstaller(tk.Tk):
    """UI class for dependency installation."""

    def __init__(self):
        super().__init__()

        self.packages: dict
        self.message = tk.StringVar(name="message")
        self.progress = tk.IntVar(value=1)

        self.title = f"{resource.settings.title} | Installer"
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.config(cursor="wait")
        self.geometry("300x90")
        self.eval(f"tk::PlaceWindow {self.winfo_toplevel()} center")

        self.lbl = ttk.Label(
            self,
            textvariable=self.message,
        )
        self.progress_bar = ttk.Progressbar(
            self,
            orient=tk.HORIZONTAL,
            length=270,
            mode="indeterminate",
            variable=self.progress,
        )
        self.lbl.grid(row=0, column=0, padx=(15, 3), pady=(15, 3), sticky="w")
        self.progress_bar.grid(row=1, column=0, padx=(15, 3), pady=(15, 3))
        self.progress_bar.start()
        self.progress_bar.focus()

    def _install_pip(self) -> None:
        """Installs python packages using pip."""
        for index, key in enumerate(self.packages.keys()):
            python_exe = sys.executable
            if VENV_PYTHONW in python_exe:
                python_exe = python_exe.replace(VENV_PYTHONW, VENV_PYTHON)
            command = f"start /wait {python_exe} -m pip install {self.packages[key]} --no-cache-dir"
            self.message.set(
                f"Installing package {index+1} of {len(self.packages)}: {key}"
            )
            self.update_idletasks()
            with subprocess.Popen(command, shell=True) as process:
                while process.poll() is None:
                    self.update()
        self.progress_bar.stop()
        self.destroy()

    def install(self, packages: dict) -> None:
        """
        Installs all dependencies.python_exe

        Args:
            packages (dict): The packages to install. Requires a dict of "package name":"command".
        """
        self.packages = packages
        self.after(100, self._install_pip)
        self.after(250, self.focus_force)
        self.mainloop()


deps = Dependencies()
