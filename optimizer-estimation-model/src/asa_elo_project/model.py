from __future__ import annotations

import itertools
import math
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np

from asa_elo_project.data.circuit_2025 import COMPS, D, K_EST, K_NEW

Ratings = Dict[str, float]


def actual_from_z(scores: Sequence[float]) -> np.ndarray:
    s = np.asarray(scores, dtype=float)
    deltas = s - s.min()
    denom = deltas.sum()
    if denom <= 0:
        return np.ones(len(s), dtype=float) / len(s)
    return deltas / denom


def expected_scores(teams: Sequence[str], ratings: Ratings) -> np.ndarray:
    n = len(teams)
    pair_den = n * (n - 1) / 2
    raw = []
    for i, a in enumerate(teams):
        ra = ratings.get(a, 1500.0)
        total = 0.0
        for j, b in enumerate(teams):
            if i == j:
                continue
            rb = ratings.get(b, 1500.0)
            total += 1 / (1 + 10 ** ((rb - ra) / D))
        raw.append(total / pair_den)
    arr = np.asarray(raw, dtype=float)
    return arr / arr.sum()


def run_order(order: Sequence[int], scores_by_comp: Sequence[Sequence[float]]) -> Tuple[Ratings, Dict[str, int]]:
    ratings: Ratings = {}
    counts: Dict[str, int] = {}
    for c in COMPS:
        for t in c.teams:
            ratings.setdefault(t, 1500.0)
            counts.setdefault(t, 0)

    for ci in order:
        comp = COMPS[ci]
        a = actual_from_z(scores_by_comp[ci])
        e = expected_scores(comp.teams, ratings)
        n = len(comp.teams)
        for i, t in enumerate(comp.teams):
            k = K_NEW if counts[t] <= 1 else K_EST
            ratings[t] += k * (n - 1) * (a[i] - e[i])
            counts[t] += 1
    return ratings, counts


def all_orders(comp_indices: Sequence[int]) -> List[Tuple[int, ...]]:
    by_dg: Dict[int, List[int]] = {}
    for idx in comp_indices:
        by_dg.setdefault(COMPS[idx].dg, []).append(idx)

    out: List[Tuple[int, ...]] = []
    for dg_order in itertools.permutations(sorted(by_dg)):
        partials: List[Tuple[int, ...]] = [tuple()]
        for dg in dg_order:
            partials = [
                p + local
                for p in partials
                for local in itertools.permutations(by_dg[dg])
            ]
        out.extend(partials)
    return out


ORDERS_07 = all_orders(list(range(5)))
ORDERS_20 = all_orders(list(range(8)))


def avg_snapshot(scores_by_comp: Sequence[Sequence[float]], which: str) -> Ratings:
    orders = ORDERS_07 if which == "07" else ORDERS_20
    acc: Ratings = {}
    for order in orders:
        r, _ = run_order(order, scores_by_comp)
        for t, v in r.items():
            acc[t] = acc.get(t, 0.0) + v
    n = len(orders)
    return {t: v / n for t, v in acc.items()}


def sorted_standings(ratings: Ratings) -> List[Tuple[str, float]]:
    return sorted(ratings.items(), key=lambda kv: -kv[1])


def rmse(pred: Ratings, known: Dict[str, float]) -> float:
    return math.sqrt(sum((pred.get(t, 1500.0) - v) ** 2 for t, v in known.items()) / len(known))
