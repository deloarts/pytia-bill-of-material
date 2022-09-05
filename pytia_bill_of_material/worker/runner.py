"""
    Runner for the main task.
"""

from tkinter import DoubleVar, Tk, ttk
from typing import Callable, List

from models.runner import RunnerModel
from pytia.log import log


class Runner:
    def __init__(
        self, root: Tk, callback_variable: DoubleVar, progress_bar: ttk.Progressbar
    ) -> None:
        self.root = root
        self.progress_callback = callback_variable
        self.progress_bar = progress_bar

        self.runners: List[RunnerModel] = []

    def add(self, func: Callable, name: str, **kwargs) -> None:
        self.runners.append(RunnerModel(func=func, name=name, kwargs=kwargs))

    def run_tasks(self) -> None:
        self.progress_bar.grid()
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
        self.progress_callback.set(value)
        self.root.update_idletasks()
