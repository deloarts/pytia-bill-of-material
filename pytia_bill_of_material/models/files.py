"""
    FILE models.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, kw_only=True)
class FileUtilityDeleteModel:
    deleted: bool = False
    skipped: bool = False

    path: Path
    ask_retry: bool
    skip_silent: bool
    at_exit: bool


@dataclass(slots=True, kw_only=True)
class FileUtilityMoveModel:
    moved: bool = False
    skipped: bool = False

    source: Path
    target: Path
    delete_existing: bool
    ask_retry: bool
    delete_skipped: bool
