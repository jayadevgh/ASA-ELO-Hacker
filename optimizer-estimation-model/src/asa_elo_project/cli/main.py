from __future__ import annotations

import argparse
from pathlib import Path

from asa_elo_project.fitting import infer_scores_from_joint_fit, joint_loss
from asa_elo_project.html_patch import patch_html_scores
from asa_elo_project.reporting import build_report, dump_fit_json_text


def main() -> None:
    parser = argparse.ArgumentParser(prog="asa-elo", description="ASA ELO simulator + reverse-engineering toolkit")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("report", help="Print standings, RMSEs, and inferred S_actual summaries")

    dump = sub.add_parser("dump-json", help="Export fitted scores + S_actual + metadata as JSON")
    dump.add_argument("--out", default="-", help="Output file path (default: stdout)")

    patch = sub.add_parser("patch-html", help="Patch an HTML simulator file with fitted score arrays")
    patch.add_argument("input_html")
    patch.add_argument("output_html")

    fitdiag = sub.add_parser("fit-diagnostics", help="Print joint-loss diagnostics for current fitted preset")

    args = parser.parse_args()
    cmd = args.cmd or "report"

    if cmd == "report":
        print(build_report())
        return

    if cmd == "dump-json":
        txt = dump_fit_json_text()
        if args.out == "-":
            print(txt)
        else:
            Path(args.out).write_text(txt, encoding="utf-8")
            print(f"Wrote {args.out}")
        return

    if cmd == "patch-html":
        out = patch_html_scores(args.input_html, args.output_html, infer_scores_from_joint_fit())
        print(f"Wrote {out}")
        return

    if cmd == "fit-diagnostics":
        scores = infer_scores_from_joint_fit()
        loss, diag = joint_loss(scores)
        print(f"joint_loss={loss:.6f}")
        print(f"rmse_0207={diag.rmse_0207:.6f}")
        print(f"rmse_0220={diag.rmse_0220:.6f}")
        print(f"hum_0207={diag.hum_0207:.6f}")
        print(f"hum_0220={diag.hum_0220:.6f}")
        return


if __name__ == "__main__":
    main()
