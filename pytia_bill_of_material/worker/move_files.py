"""
    Moves all files to their destination.
"""

from protocols.task_protocol import TaskProtocol
from pytia.log import log
from utils.files import file_utility

from .runner import Runner


class MoveFilesTask(TaskProtocol):
    """
    Moves all files to their destination after the export.

    Args:
        TaskProtocol (_type_): The task runner protocol.
    """

    __slots__ = "_runner"

    def __init__(self, runner: Runner) -> None:
        """
        Inits the class.

        Args:
            runner (Runner): The runner instance for handling UI elements.
        """
        self._runner = runner

    def run(self) -> None:
        """Runs the task."""
        log.info("Moving files.")
        for item in file_utility.move_items:
            self._runner.add(
                func=file_utility.move_item,
                name=f"Moving file {item.target.name!r}",
                item=item,
            )
        self._runner.run_tasks()
        file_utility.delete_all()
