"""
    Runner for the main task.
"""

from tkinter import DoubleVar
from tkinter import Tk
from typing import Callable
from typing import List

from models.runner import RunnerModel
from pytia.log import log


class Runner:
    """
    This class is responsible for running tasks and updating the UI.
    """

    def __init__(
        self,
        root: Tk,
        callback_variable: DoubleVar,
    ) -> None:
        self.root = root
        self.progress_callback = callback_variable

        self.runners: List[RunnerModel] = []

    def add(self, func: Callable, name: str, **kwargs) -> None:
        """
        Add a task function. Functions must be task-protocol-functions.

        Args:
            func (Callable): The task to be queued.
            name (str): The name of the task.

        Kwargs:
            Will be passed to the task function.
        """
        self.runners.append(RunnerModel(func=func, name=name, kwargs=kwargs))

    def run_tasks(self) -> None:
        """Runs all queued tasks."""
        self._update_progress(1)
        for fn in self.runners:
            log.info(f"Running task {fn.name!r}.")
            fn.func(**fn.kwargs)
            self._update_progress(
                self.progress_callback.get() + int(100 / len(self.runners))
            )
            self.root.update_idletasks()
        self._update_progress(100)

    def _update_progress(self, value: int | float) -> None:
        """Update the progress bar."""
        self.progress_callback.set(value)
        self.root.update_idletasks()
