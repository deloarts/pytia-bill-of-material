"""
    Builds the app using zipapp.
    Exports to the build folder.
"""

import json
import os
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

from pytia_bill_of_material.const import APP_NAME, APP_VERSION

settings_path = "./pytia_bill_of_material/resources/settings.json"
branch_name = Repository(".").head.shorthand


class Build:
    def __init__(self) -> None:
        if not os.path.exists(settings_path):
            raise Exception(
                f"Config file 'settings.json' not found. "
                f"Have you followed the setup instructions?"
            )
        with open(settings_path, "r") as f:
            self.settings = json.load(f)

        self.dev_build = bool(branch_name == "development" or self.settings["debug"])
        self.source_folder = Path("./pytia_bill_of_material").resolve()
        self.build_folder = Path("./build").resolve()

        self.build_app_path = (
            Path(self.build_folder, self.settings["files"]["app"])
            if not self.dev_build
            else Path(self.build_folder, "dev_app.pyz")
        )
        self.build_launcher_path = (
            Path(self.build_folder, self.settings["files"]["launcher"])
            if not self.dev_build
            else Path(self.build_folder, "dev_launcher.catvbs")
        )
        self.release_app_path = (
            WindowsPath(
                self.settings["paths"]["release"], self.settings["files"]["app"]
            )
            if not self.dev_build
            else WindowsPath(self.build_folder, "dev_app.pyz")
        )

    def provide(self):
        os.makedirs(self.build_folder, exist_ok=True)
        for item in os.listdir(self.build_folder):
            os.remove(Path(self.build_folder, item))

    @staticmethod
    def test():
        code = pytest.main()
        if code == pytest.ExitCode.TESTS_FAILED:
            print("\n\nCannot build app: Tests are failing.\n\n")
            sys.exit(2)

    @staticmethod
    def get_required_version() -> Tuple[int, int]:
        with open("./pyproject.toml", "r") as f:
            pyproject = toml.load(f)
        ppv = pyproject["tool"]["poetry"]["dependencies"]["python"]
        v = Version("".join([i for i in ppv if str(i).isdigit() or i == "."]))
        return v.major, v.minor

    def create_launcher(self):
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
            os.remove(self.build_launcher_path)
        with open(self.build_launcher_path, "w") as f:
            f.write(catvbs)

    def build(self):
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
        print(f"\n\nBuilt app into {self.build_folder}\n\n")


if __name__ == "__main__":
    print(f"Building {APP_NAME} {APP_VERSION}\n")
    builder = Build()
    builder.build()
