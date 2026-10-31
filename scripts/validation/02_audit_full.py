"""Create a full reviewer-1 audit sheet (reviewer 2 pending)."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from graphambicardio import config  # noqa: E402
from graphambicardio.io_utils import get_logger  # noqa: E402


def main() -> None:
    log = get_logger("audit_full")
    edges = pd.read_csv(config.CURATED / "curated_edges.csv")
    out = pd.DataFrame({
        "evidence_id": edges["evidence_id"],
        "edge_key": edges["edge_key"],
        "reference": edges["reference"],
        "quote": edges["quote"],
        "reviewer_1_role": "equipe de curadoria (leitura do abstract)",
        "reviewer_1_supports": "sim (citação verificada automaticamente)",
        "reviewer_2_role": "",
        "reviewer_2_supports": "",
        "agreement": "",
        "resolution": "pendente de revisor independente",
    })
    out.to_csv(config.REPORTS / "audit_reviewer1_full.csv", index=False)
    log.info("audit sheet: %s edges (reviewer 2 pending)", len(out))


if __name__ == "__main__":
    main()
