from __future__ import annotations

import json
from typing import Dict, List, Sequence

from asa_elo_project.data.circuit_2025 import COMPS, KNOWN_0207, KNOWN_0220
from asa_elo_project.fitting import infer_scores_from_joint_fit, joint_loss
from asa_elo_project.model import ORDERS_07, ORDERS_20, actual_from_z, avg_snapshot, rmse, sorted_standings


def build_report(scores_by_comp=None) -> str:
    if scores_by_comp is None:
        scores_by_comp = infer_scores_from_joint_fit()
    r07 = avg_snapshot(scores_by_comp, "07")
    r20 = avg_snapshot(scores_by_comp, "20")
    _, diag = joint_loss(scores_by_comp)

    lines: List[str] = []
    lines.append(f"Permutations: 02/07={len(ORDERS_07)}, 02/20={len(ORDERS_20)}")
    lines.append(f"RMSE 02/07 = {rmse(r07, KNOWN_0207):.6f}")
    lines.append(f"RMSE 02/20 = {rmse(r20, KNOWN_0220):.6f}")
    lines.append(f"Joint loss (diagnostic) = {diag.loss:.6f}")
    lines.append("")

    for label, ratings in [("02/07", r07), ("02/20", r20)]:
        lines.append(f"Top 12 @ {label}")
        for i, (team, value) in enumerate(sorted_standings(ratings)[:12], 1):
            lines.append(f"{i:2d}. {team:22s} {value:8.2f}")
        lines.append("")

    for key in ["jeena", "awaazein", "boston_bandish"]:
        comp = next(c for c in COMPS if c.key == key)
        z = next(scores_by_comp[i] for i, c in enumerate(COMPS) if c.key == key)
        a = actual_from_z(z)
        lines.append(f"[{key}] top inferred S_actual")
        order = sorted(range(len(comp.teams)), key=lambda j: -z[j])
        for j in order[:5]:
            lines.append(f"  {comp.teams[j]:22s} z={z[j]:8.4f} S_actual={a[j]:.4f}")
        lines.append("")

    return "\n".join(lines)


def dump_fit_json(scores_by_comp=None) -> Dict:
    if scores_by_comp is None:
        scores_by_comp = infer_scores_from_joint_fit()
    r07 = avg_snapshot(scores_by_comp, "07")
    r20 = avg_snapshot(scores_by_comp, "20")
    return {
        "rmse_0207": rmse(r07, KNOWN_0207),
        "rmse_0220": rmse(r20, KNOWN_0220),
        "orders_0207": len(ORDERS_07),
        "orders_0220": len(ORDERS_20),
        "scores_by_comp": {
            c.key: [float(x) for x in scores_by_comp[i]] for i, c in enumerate(COMPS)
        },
        "s_actual_by_comp": {
            c.key: {t: float(v) for t, v in zip(c.teams, actual_from_z(scores_by_comp[i]))}
            for i, c in enumerate(COMPS)
        },
    }


def dump_fit_json_text(scores_by_comp=None) -> str:
    return json.dumps(dump_fit_json(scores_by_comp), indent=2)
