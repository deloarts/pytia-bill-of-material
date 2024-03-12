"""
    Moves all files to their destination.
"""

import os
from pathlib import Path

from app.main.vars import Variables
from const import BOM
from const import BUNDLE
from const import DOCKETS
from const import DOCUMENTATION
from const import DRAWINGS
from const import JPGS
from const import STLS
from const import STPS
from protocols.task_protocol import TaskProtocol
from pytia.log import log
from pytia_ui_tools.utils.files import file_utility

from .runner import Runner


class MoveFilesTask(TaskProtocol):
    """
    Moves all files to their destination after the export.

    Args:
        TaskProtocol (_type_): The task runner protocol.
    """

    __slots__ = "_runner"

    def __init__(self, runner: Runner, export_root_path: Path, vars: Variables) -> None:
        """
        Inits the class.

        Args:
            runner (Runner): The runner instance for handling UI elements.
        """
        self.runner = runner
        self.export_root_path = export_root_path
        self.vars = vars

    def run(self) -> None:
        """Runs the task."""
        log.info("Moving files.")

        self._add_move(
            category=BOM, target=Path(self.vars.bom_export_path.get()).parent
        )
        self._add_move(
            category=DOCUMENTATION,
            target=Path(self.vars.documentation_export_path.get()),
        )

        if self.vars.bundle.get():
            self._add_move(
                category=BUNDLE, target=Path(self.vars.bundle_export_path.get())
            )
        else:
            self._add_move(
                category=DOCKETS, target=Path(self.vars.docket_export_path.get())
            )
            self._add_move(
                category=DRAWINGS, target=Path(self.vars.drawing_export_path.get())
            )
            self._add_move(category=STLS, target=Path(self.vars.stl_export_path.get()))
            self._add_move(category=STPS, target=Path(self.vars.stp_export_path.get()))
            self._add_move(category=JPGS, target=Path(self.vars.jpg_export_path.get()))

        for item in file_utility.move_items:
            self.runner.add(
                func=file_utility.move_item,
                name=f"Moving file {item.target.name!r}",
                item=item,
            )
        for item in file_utility.delete_items:
            self.runner.add(
                func=file_utility.delete_item,
                name=f"Deleting file {str(item.path)!r}",
                item=item,
            )
        self.runner.run_tasks()

    def _add_move(self, category: str, target: Path) -> None:
        p = Path(self.export_root_path, category)
        for item in os.listdir(p):
            s = Path(p, item)
            t = Path(target, item) if target.is_dir() else target
            if s.is_file():
                file_utility.add_move(source=s, target=t)
