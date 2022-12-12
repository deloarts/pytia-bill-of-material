"""
    Releases the app to the specified folder.
"""

import json
import os
import re
import shutil
import sys
from pathlib import Path

from pygit2 import Repository
from pytia.console import Console

from pytia_bill_of_material.const import APP_NAME, APP_VERSION

console = Console()
settings_path = Path("./pytia_bill_of_material/resources/settings.json").resolve()
branch_name = Repository(".").head.shorthand


class Release:
    def __init__(self) -> None:
        if not os.path.exists(settings_path):
            console.error(
                "Config file not found. Have you followed the setup instructions?"
            )
            sys.exit()

        with open(settings_path, "r") as f:
            self.settings = json.load(f)

        if not re.match(
            r"^v\d+(\.\d+){2,3}$", branch_name
        ) and not branch_name.lower() in ["head", "main"]:
            console.error(
                f"Cannot release from branch {branch_name!r}. "
                "Please switch branch to a release tag."
            )
            sys.exit()

    def provide(self):
        console.info("Providing folders ...")

        self.source_app = Path(f"./build/{self.settings['files']['app']}").resolve()
        console.info(f"App build source is {str(self.source_app)!r}")

        self.source_launcher = Path(
            f"./build/{self.settings['files']['launcher']}"
        ).resolve()
        console.info(f"Launcher build source is {str(self.source_launcher)!r}")

        self.target_app = (
            f"{self.settings['paths']['release']}/{self.settings['files']['app']}"
        )
        console.info(f"App release path is {str(self.target_app)!r}")

        self.target_launcher = (
            f"{self.settings['paths']['release']}/{self.settings['files']['launcher']}"
        )
        console.info(f"Launcher release path is {str(self.target_launcher)!r}")

    def move_files(self):
        if os.path.exists(self.source_app) and os.path.exists(self.source_app):
            console.info("Moving files ...")
            shutil.move(self.source_app, self.target_app)
            shutil.move(self.source_launcher, self.target_launcher)
        else:
            console.error("Failed: No build file.")
            sys.exit()

    def switch_branch(self):
        git_repo = Repository(".git")
        branch = git_repo.lookup_branch("development")
        ref = git_repo.lookup_reference(branch.name)
        git_repo.checkout(ref)
        console.info(f"Switched branch to development")

    def release(self) -> None:
        console.info(f"Releasing {APP_NAME} {APP_VERSION}")
        self.provide()
        self.move_files()
        self.switch_branch()
        console.ok(f"App released to {self.settings['paths']['release']}")


if __name__ == "__main__":
    releaser = Release()
    releaser.release()
