from asa_elo_project.fitting import infer_scores_from_joint_fit
from asa_elo_project.model import avg_snapshot
from asa_elo_project.data.circuit_2025 import KNOWN_0207, KNOWN_0220


def test_snapshots_compute():
    scores = infer_scores_from_joint_fit()
    r07 = avg_snapshot(scores, "07")
    r20 = avg_snapshot(scores, "20")
    for t in ["Dhamakapella", "TAMU Swaram", "UCD Jhankaar"]:
        assert t in r07 and t in r20
    # basic sanity around expected magnitude
    assert abs(r07["Dhamakapella"] - KNOWN_0207["Dhamakapella"]) < 2.0
    assert abs(r20["UW Awaaz"] - KNOWN_0220["UW Awaaz"]) < 2.0
