"""Fase B/F: structured biological databases (HPO, NCBI Gene, ClinVar, Reactome, Enrichr)."""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from graphambicardio import config  # noqa: E402
from graphambicardio.databases import clinvar, enrichr, hpo, ncbigene, reactome  # noqa: E402
from graphambicardio.io_utils import get_logger, utc_now, write_json  # noqa: E402


def main() -> None:
    log = get_logger("collect_databases")
    log.info("start %s", utc_now())

    hpo.fetch_term_metadata()
    edges = hpo.gene_phenotype_edges()

    counts = Counter(e["gene_symbol"] for e in edges)
    hpo_genes = [g for g, _ in counts.most_common(150)]
    panel = sorted(set(config.GENE_PANEL))
    genes = sorted(set(panel) | set(hpo_genes))
    write_json(config.DATA_PROCESSED / "gene_universe.json", {"panel": panel, "hpo_top150": hpo_genes, "n_union": len(genes)})

    ncbigene.collect(genes)
    clinvar.collect_genes(panel, per_gene=30)
    reactome.collect_genes(genes)
    try:
        uid = enrichr.add_list(genes)
        enrichr.enrich(uid, "GO_Biological_Process_2023")
    except Exception as exc:  # noqa: BLE001
        log.warning("Enrichr failed: %s", exc)

    log.info("done %s", utc_now())


if __name__ == "__main__":
    main()
