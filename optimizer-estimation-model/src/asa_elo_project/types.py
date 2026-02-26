from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Competition:
    key: str
    dg: int  # date-group index for permutation averaging
    teams: List[str]
    seed: List[float]
    placements: Dict[str, int]
