"""
    Builds the app using zipapp.
    Exports to the build folder.
"""

import json
import os
import re
import sys
import zipapp
from datetime import datetime
from pathlib import Path, WindowsPath
from typing import Tuple

import pytest
import toml
from jinja2 import Environment, FileSystemLoader
from packaging.version import Version
from pygit2 import Repository
from pytia.console import Console

from pytia_bill_of_material.const import APP_NAME, APP_VERSION

console = Console()
settings_path = Path("./pytia_bill_of_material/resources/settings.json").resolve()
branch_name = Repository(".").head.shorthand


class Build:
    def __init__(self) -> None:
        if not os.path.exists(settings_path):
            console.error("Config file not found. Have you followed the setup instructions?")
            sys.exit()

        with open(settings_path, "r") as f:
            self.settings = json.load(f)

        self.dev_build = bool(
            self.settings["debug"]
            or (not re.match(r"^v\d+(\.\d+){2,3}$", branch_name) and not branch_name.lower() in ["head", "main"])
        )
        if self.dev_build:
            console.warning(f"App is built in development mode from branch {branch_name!r}")

    def provide(self):
        console.info("Providing folders ...")

        self.source_folder = Path("./pytia_bill_of_material").resolve()
        console.info(f"Source folder is {str(self.source_folder)!r}")

        self.build_folder = Path("./build").resolve()
        console.info(f"Build folder is {str(self.build_folder)!r}")

        self.build_app_path = (
            Path(self.build_folder, self.settings["files"]["app"])
            if not self.dev_build
            else Path(self.build_folder, "dev_app.pyz")
        )
        console.info(f"App build path is {str(self.build_app_path)!r}")

        self.build_launcher_path = (
            Path(self.build_folder, self.settings["files"]["launcher"])
            if not self.dev_build
            else Path(self.build_folder, "dev_launcher.catvbs")
        )
        console.info(f"Launcher build path is {str(self.build_launcher_path)!r}")

        self.release_app_path = (
            WindowsPath(self.settings["paths"]["release"], self.settings["files"]["app"])
            if not self.dev_build
            else WindowsPath(self.build_folder, "dev_app.pyz")
        )
        console.info(f"VBA embedded release is {str(self.release_app_path)!r}")

        os.makedirs(self.build_folder, exist_ok=True)
        for item in os.listdir(self.build_folder):
            os.remove(Path(self.build_folder, item))

    @staticmethod
    def test():
        console.info("Running tests ...")
        code = pytest.main()
        if code == pytest.ExitCode.TESTS_FAILED:
            console.error("Failed building app: Tests are failing.")
            sys.exit()

    @staticmethod
    def get_required_version() -> Tuple[int, int]:
        console.info("Acquiring app version ...")
        with open("./pyproject.toml", "r") as f:
            pyproject = toml.load(f)
        ppv = pyproject["tool"]["poetry"]["dependencies"]["python"]
        v = Version("".join([i for i in ppv if str(i).isdigit() or i == "."]))
        return v.major, v.minor

    def create_launcher(self):
        console.info("Creating launcher file ...")
        major, minor = self.get_required_version()

        file_loader = FileSystemLoader("./vbs")
        env = Environment(loader=file_loader)

        template = env.get_template("build.template.catvbs")
        catvbs = template.render(
            creator=os.environ.get("USERNAME"),
            date=datetime.now(),
            path=self.release_app_path,
            launcher=self.settings["files"]["launcher"],
            major=major,
            minor=minor,
            settings=self.settings,
            title=self.settings["title"],
            version=APP_VERSION,
        )

        if os.path.exists(self.build_launcher_path):
            console.info(f"Removing existing file {str(self.build_launcher_path)!r}")
            os.remove(self.build_launcher_path)

        with open(self.build_launcher_path, "w") as f:
            f.write(catvbs)
        console.info(f"Saved new launcher as {str(self.build_launcher_path)!r}")

    def build(self):
        console.info(f"Building {APP_NAME} {APP_VERSION}")
        self.provide()
        self.test()
        self.create_launcher()
        zipapp.create_archive(
            source=self.source_folder,
            target=self.build_app_path,
            interpreter=None,
            main=None,
            filter=None,
            compressed=False,
        )
        console.ok(f"Built app into {str(self.build_folder)!r}")


if __name__ == "__main__":
    builder = Build()
    builder.build()
