"""
    PATHS data models.
"""

# pylint: disable=C0116

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict


@dataclass(kw_only=True, slots=True)
class Paths:
    items: Dict[str, Path] = field(default_factory=dict)
