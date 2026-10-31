"""Re-run ClinVar (fixed parser) and Enrichr for the curated gene universe."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from graphambicardio import config  # noqa: E402
from graphambicardio.databases import clinvar, enrichr  # noqa: E402
from graphambicardio.io_utils import get_logger, read_json  # noqa: E402


def main() -> None:
    log = get_logger("clinvar_enrichr")
    clinvar.collect_genes(sorted(set(config.GENE_PANEL)), per_gene=50)
    universe = read_json(config.DATA_PROCESSED / "gene_universe.json")
    genes = sorted(set(universe["panel"]) | set(universe["hpo_top150"]))
    try:
        uid = enrichr.add_list(genes)
        enrichr.enrich(uid, "GO_Biological_Process_2023")
    except Exception as exc:  # noqa: BLE001
        log.warning("Enrichr failed: %s", exc)


if __name__ == "__main__":
    main()
