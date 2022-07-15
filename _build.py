"""
    Builds the app using zipapp.
    Exports to the build folder.
"""

import json
import os
import sys
import zipapp
from datetime import datetime
from typing import Tuple

import pytest
import toml
from jinja2 import Environment, FileSystemLoader
from packaging.version import Version

from pytia_bill_of_material.const import APP_NAME, APP_VERSION

settings_path = "./pytia_bill_of_material/resources/settings.json"


class Build:
    def __init__(self) -> None:
        if not os.path.exists(settings_path):
            raise Exception(
                f"Config file 'settings.json' not found. "
                f"Have you followed the setup instructions?"
            )
        with open(settings_path, "r") as f:
            self.settings = json.load(f)

        self.source = f"./pytia_bill_of_material"
        self.target_folder = f"./build"
        self.target_app = f"{self.target_folder}/{self.settings['files']['app']}"
        self.target_launcher = (
            f"{self.target_folder}/{self.settings['files']['launcher']}"
        )

    @staticmethod
    def provide():
        os.makedirs("./build", exist_ok=True)

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
        path = f"{self.settings['paths']['release']}\\{self.settings['files']['app']}"
        major, minor = self.get_required_version()

        file_loader = FileSystemLoader("./vbs")
        env = Environment(loader=file_loader)

        template = env.get_template("build.template.catvbs")
        catvbs = template.render(
            creator=os.environ.get("USERNAME"),
            date=datetime.now(),
            path=path,
            launcher=self.settings["files"]["launcher"],
            major=major,
            minor=minor,
            settings=self.settings,
            title=self.settings["title"],
            version=APP_VERSION,
        )

        if os.path.exists(self.target_launcher):
            os.remove(self.target_launcher)
        with open(self.target_launcher, "w") as f:
            f.write(catvbs)

    def build(self):
        self.provide()
        self.test()
        self.create_launcher()
        zipapp.create_archive(
            source=self.source,
            target=self.target_app,
            interpreter=None,
            main=None,
            filter=None,
            compressed=False,
        )
        print(f"\n\nBuilt app into {self.target_folder}\n\n")


if __name__ == "__main__":
    print(f"Building {APP_NAME} {APP_VERSION}\n")
    builder = Build()
    builder.build()
