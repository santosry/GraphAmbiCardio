"""Entity-resolution audit: check identifiers, duplicates and missing external IDs."""
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from graphambicardio import config  # noqa: E402
from graphambicardio.io_utils import get_logger, write_csv  # noqa: E402


def main() -> None:
    log = get_logger("normalize")
    nodes = pd.read_csv(config.GRAPH_OUT / "nodes.csv").fillna("")
    rows = []
    for _, n in nodes.iterrows():
        external = bool(str(n["identifiers"]).strip())
        rows.append({
            "node_id": n["node_id"],
            "type": n["type"],
            "label": n["label"],
            "has_external_id": external,
            "identifiers": n["identifiers"],
            "issue": "" if external or n["type"] in {"Exposure", "Mechanism", "Process", "Indicator", "Population", "Period"} else "missing_external_identifier",
        })
    df = pd.DataFrame(rows)
    df.to_csv(config.DATA_PROCESSED / "entity_resolution_report.csv", index=False)
    summary = {
        "n_nodes": len(df),
        "missing_external_id_by_type": df[df["issue"] != ""].groupby("type").size().to_dict(),
        "duplicate_labels_within_type": {
            f"{t}::{lab}": c
            for (t, lab), c in Counter(zip(df["type"], df["label"])).items()
            if c > 1 and t in {"Phenotype", "Exposure", "Mechanism", "Process"}
        },
    }
    write_csv(config.REPORTS / "entity_resolution_summary.csv", [{"metric": k, "value": str(v)} for k, v in summary.items()])
    log.info("entity resolution: %s nodes, missing external IDs: %s", len(df), summary["missing_external_id_by_type"])


if __name__ == "__main__":
    main()
