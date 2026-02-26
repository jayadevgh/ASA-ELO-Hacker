# ASA ELO Project

A reproducible Python project for simulating the ASA ELO algorithm and reverse-engineering plausible competition score distributions (`S_actual`) from public leaderboard snapshots.

This project includes:
- **ASA ELO simulator** (expected scores, actual scores from normalized z-scores, K-factor updates)
- **Date-group permutation averaging** (to mimic same-day ordering uncertainty)
- **Joint snapshot evaluation** (02/07 and 02/20 standings)
- **Preset joint-constrained fit** (the fitted z-score arrays we derived)
- **CLI tools** for reports, JSON exports, and HTML patching
- **Starter fitter scaffold** so you can extend into a full optimization project

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
asa-elo report
```

## Example commands

```bash
# print standings + RMSE + inferred S_actual highlights
asa-elo report

# export all fitted z-scores and S_actual as JSON
asa-elo dump-json --out fit_dump.json

# patch an HTML simulator file with fitted score arrays
asa-elo patch-html input.html output.html
```

## Project layout

- `src/asa_elo_project/data/circuit_2025.py` — competitions, snapshots, fitted scores
- `src/asa_elo_project/model.py` — ELO math + permutation averaging
- `src/asa_elo_project/reporting.py` — report helpers / summaries
- `src/asa_elo_project/fitting.py` — starter scaffold for optimization experiments
- `src/asa_elo_project/html_patch.py` — inject fitted scores into your simulator HTML
- `src/asa_elo_project/cli/main.py` — command line interface
- `tests/` — smoke tests

## Notes

- The included fitted scores are **a valid joint-constrained fit**, not unique ground truth.
- The inverse problem is underdetermined; many z-score configurations can reproduce similar standings.
- The current fitter module is intentionally lightweight and extensible, not a polished optimizer.

## Next upgrades (fun math dragon stuff)

- Add SciPy-based constrained optimization with explicit membership/order penalties
- Sample multiple fits and compute uncertainty bands for inferred `S_actual`
- Compare ASA K-factor variants (`K_NEW/K_EST` vs flat K)
- Add a small web app / notebook visualization layer
