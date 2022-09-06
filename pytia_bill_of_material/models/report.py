"""
    REPORT data models.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from const import Status


@dataclass
class ReportItem:
    partnumber: str
    path: Path | None
    parent_path: Path
    details: Dict[str, Status] = field(default_factory=dict)
    status: Status = field(default=Status.OK)


@dataclass
class Report:
    status: Status = field(default=Status.OK)
    items: List[ReportItem] = field(default_factory=list)
