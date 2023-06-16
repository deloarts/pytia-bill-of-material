"""
    Moves all files to their destination.
"""

import os
from pathlib import Path

from const import BOM, DOCKETS, DRAWINGS, JPGS, STLS, STPS
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

    def __init__(
        self,
        runner: Runner,
        export_root_path: Path,
        bom_export_path: Path,
        drawing_export_path: Path,
        docket_export_path: Path,
        stp_export_path: Path,
        stl_export_path: Path,
        jpg_export_path: Path,
    ) -> None:
        """
        Inits the class.

        Args:
            runner (Runner): The runner instance for handling UI elements.
        """
        self.runner = runner
        self.export_root_path = export_root_path
        self.bom_export_path = bom_export_path.parent
        self.drawing_export_path = drawing_export_path
        self.docket_export_path = docket_export_path
        self.stp_export_path = stp_export_path
        self.stl_export_path = stl_export_path
        self.jpg_export_path = jpg_export_path

    def run(self) -> None:
        """Runs the task."""
        log.info("Moving files.")

        self._add_move(category=BOM, target=self.bom_export_path)
        self._add_move(category=DOCKETS, target=self.docket_export_path)
        self._add_move(category=DRAWINGS, target=self.drawing_export_path)
        self._add_move(category=STLS, target=self.stl_export_path)
        self._add_move(category=STPS, target=self.stp_export_path)
        self._add_move(category=JPGS, target=self.jpg_export_path)

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
        for item in os.listdir(Path(self.export_root_path, category)):
            file_utility.add_move(
                Path(self.export_root_path, category, item),
                Path(target, item) if target.is_dir() else target,
            )
