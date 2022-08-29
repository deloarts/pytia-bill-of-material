"""
    BOM object data model.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List


@dataclass(kw_only=True, slots=True)
class BOMAssemblyItem:
    partnumber: str
    properties: dict
    path: Path


@dataclass(kw_only=True, slots=True)
class BOMAssembly:
    partnumber: str
    path: Path
    items: List[BOMAssemblyItem] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class BOM:
    created: datetime = field(init=False, default_factory=lambda: datetime.now())
    assemblies: List[BOMAssembly] = field(default_factory=list)
    summary: BOMAssembly = field(default=None)  # type: ignore
