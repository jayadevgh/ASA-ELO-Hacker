from __future__ import annotations

"""Starter fitting scaffolds for reverse-engineering z-scores.

This module intentionally provides **project-grade structure** rather than a polished optimizer.
It includes:
- utilities to decode score arrays
- a joint loss function over 02/07 and 02/20 snapshots
- simple penalty helpers for top-10 membership constraints

You can plug in SciPy optimization routines (L-BFGS-B, Powell, coordinate descent, etc.) on top.
"""

from dataclasses import dataclass
from typing import Dict, List, Sequence

import numpy as np

from asa_elo_project.data.circuit_2025 import (
    COMPS,
    JOINT_FIT_SCORES,
    KNOWN_0207,
    KNOWN_0220,
    TOP10_0207,
    TOP10_0220,
)
from asa_elo_project.model import avg_snapshot, rmse


@dataclass
class JointFitDiagnostics:
    rmse_0207: float
    rmse_0220: float
    hum_0207: float | None = None
    hum_0220: float | None = None
    loss: float | None = None


def infer_scores_from_joint_fit() -> List[np.ndarray]:
    return [np.array(JOINT_FIT_SCORES[c.key], dtype=float) for c in COMPS]


def hinge_sq(x: float) -> float:
    return x * x if x > 0 else 0.0


def joint_loss(
    scores_by_comp: Sequence[Sequence[float]],
    exact_weight: float = 1.0,
    membership_weight: float = 200.0,
    margin_0207: float = 0.02,
    margin_0220: float = 0.02,
) -> tuple[float, JointFitDiagnostics]:
    """Evaluate joint constrained loss across both leaderboard snapshots.

    This reproduces the *style* of fitting used in the exploration:
    - squared error on known ratings
    - penalties for non-top10 teams crossing the cutoff threshold
    """
    r07 = avg_snapshot(scores_by_comp, "07")
    r20 = avg_snapshot(scores_by_comp, "20")

    loss = 0.0
    for t, v in KNOWN_0207.items():
        loss += exact_weight * (r07.get(t, 1500.0) - v) ** 2
    for t, v in KNOWN_0220.items():
        loss += exact_weight * (r20.get(t, 1500.0) - v) ** 2

    cutoff07 = KNOWN_0207["Stanford Raagapella"] - margin_0207
    cutoff20 = KNOWN_0220["Illini Awaaz"] - margin_0220
    top07 = set(TOP10_0207)
    top20 = set(TOP10_0220)

    for t, val in r07.items():
        if t not in top07:
            loss += membership_weight * hinge_sq(val - cutoff07)
    for t, val in r20.items():
        if t not in top20:
            loss += membership_weight * hinge_sq(val - cutoff20)

    diag = JointFitDiagnostics(
        rmse_0207=rmse(r07, KNOWN_0207),
        rmse_0220=rmse(r20, KNOWN_0220),
        hum_0207=r07.get("Hum A Cappella"),
        hum_0220=r20.get("Hum A Cappella"),
        loss=loss,
    )
    return loss, diag


def coordinate_descent_stub(
    initial_scores: Sequence[Sequence[float]] | None = None,
) -> List[np.ndarray]:
    """Placeholder/starter for your own optimization experiments.

    Right now this just returns the preset joint fit so the package is runnable end-to-end.
    Replace with your favorite optimizer and call `joint_loss(...)` as the objective.
    """
    if initial_scores is None:
        return infer_scores_from_joint_fit()
    return [np.array(s, dtype=float) for s in initial_scores]
