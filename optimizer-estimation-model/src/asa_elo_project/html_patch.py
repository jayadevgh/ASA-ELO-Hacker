from __future__ import annotations

import re
from pathlib import Path
from typing import Sequence

from asa_elo_project.data.circuit_2025 import COMPS


def patch_html_scores(input_html: str | Path, output_html: str | Path, scores_by_comp: Sequence[Sequence[float]]) -> Path:
    text = Path(input_html).read_text(encoding="utf-8")

    for comp, arr in zip(COMPS, scores_by_comp):
        arr_str = "[" + ",".join(f"{x:.6f}".rstrip("0").rstrip(".") for x in arr) + "]"
        pattern = rf'(key:"{re.escape(comp.key)}".*?scores:)\[[^\]]*\]'
        text, n = re.subn(pattern, rf"\1{arr_str}", text, count=1, flags=re.S)
        if n != 1:
            raise ValueError(f"Could not patch scores for comp key={comp.key!r}")

    # Patch snapshot averaging bug if the old function exists in the HTML scaffold.
    old_snippet = "function averageAcrossPerms(comps){"
    if old_snippet in text and "ordersCount07" not in text:
        text = re.sub(
            r"function averageAcrossPerms\(comps\)\{.*?return \{ordersCount: orders\.length, avg07, avg20\};\n\}",
            (
                "function averageAcrossPerms(comps){\n"
                "  const first5Comps = comps.slice(0,5);\n"
                "  const orders07 = allOrders(first5Comps);\n"
                "  const orders20 = allOrders(comps);\n"
                "  const acc07 = {}, acc20 = {}, cnt07 = {}, cnt20 = {};\n\n"
                "  for(const order of orders07){\n"
                "    const r07 = runSeason(order, first5Comps, null).ratings;\n"
                "    for(const [t,v] of Object.entries(r07)){\n"
                "      acc07[t] = (acc07[t] ?? 0) + v;\n"
                "      cnt07[t] = (cnt07[t] ?? 0) + 1;\n"
                "    }\n"
                "  }\n"
                "  for(const order of orders20){\n"
                "    const r20 = runSeason(order, comps, null).ratings;\n"
                "    for(const [t,v] of Object.entries(r20)){\n"
                "      acc20[t] = (acc20[t] ?? 0) + v;\n"
                "      cnt20[t] = (cnt20[t] ?? 0) + 1;\n"
                "    }\n"
                "  }\n\n"
                "  const avg07 = {}, avg20 = {};\n"
                "  for(const t of Object.keys(cnt07)) avg07[t] = acc07[t]/cnt07[t];\n"
                "  for(const t of Object.keys(cnt20)) avg20[t] = acc20[t]/cnt20[t];\n"
                "  return {ordersCount: orders20.length, ordersCount07: orders07.length, ordersCount20: orders20.length, avg07, avg20};\n"
                "}"
            ),
            text,
            count=1,
            flags=re.S,
        )
        text = text.replace(
            "Computed <b>${out.ordersCount}</b> full competition orders (date-group and same-day permutations).",
            "Computed <b>${out.ordersCount07}</b> orders for 02/07 snapshot and <b>${out.ordersCount20}</b> orders for 02/20 snapshot (with date-group + same-day permutations).",
        )

    out_path = Path(output_html)
    out_path.write_text(text, encoding="utf-8")
    return out_path
