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
            source=Path(self.export_root_path, BOM),
            target=Path(self.vars.bom_export_path.get()).parent,
        )
        self._add_move(
            source=Path(self.export_root_path, DOCUMENTATION),
            target=Path(self.vars.documentation_export_path.get()),
        )

        if self.vars.bundle.get():
            self._add_move(
                source=Path(self.export_root_path, BUNDLE),
                target=Path(self.vars.bundle_export_path.get()),
            )
        else:
            self._add_move(
                source=Path(self.export_root_path, DOCKETS),
                target=Path(self.vars.docket_export_path.get()),
            )
            self._add_move(
                source=Path(self.export_root_path, DRAWINGS),
                target=Path(self.vars.drawing_export_path.get()),
            )
            self._add_move(
                source=Path(self.export_root_path, STLS),
                target=Path(self.vars.stl_export_path.get()),
            )
            self._add_move(
                source=Path(self.export_root_path, STPS),
                target=Path(self.vars.stp_export_path.get()),
            )
            self._add_move(
                source=Path(self.export_root_path, JPGS),
                target=Path(self.vars.jpg_export_path.get()),
            )

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

    def _add_move(self, source: Path, target: Path) -> None:
        """Moves every file inside the source dir to the target dir."""
        for abs_file in source.rglob("*.*"):
            rel_file = abs_file.relative_to(source)
            target_file = Path(target, rel_file)
            os.makedirs(target_file.parent, exist_ok=True)  # TODO: Integrate this into file_utility
            file_utility.add_move(source=abs_file, target=target_file)
