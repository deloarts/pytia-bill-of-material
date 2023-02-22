"""
    RUNNER data models.
"""

# pylint: disable=C0116

from dataclasses import dataclass
from typing import Callable


@dataclass
class RunnerModel:
    func: Callable
    kwargs: dict
    name: str
