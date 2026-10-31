"""Enrichment summary and low-evidence edge inventory."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from graphambicardio import config  # noqa: E402
from graphambicardio.io_utils import get_logger, write_csv  # noqa: E402


def main() -> None:
    log = get_logger("enrichment")
    e = pd.read_csv(config.DATA_PROCESSED / "enrichr_GO_Biological_Process_2023.csv")
    e = e.sort_values(["adjusted_p_value", "term"]).head(30)
    e.to_csv(config.TABLES / "enrichr_top30.csv", index=False)

    r = pd.read_csv(config.DATA_PROCESSED / "reactome_gene_pathway_edges.csv")
    top = (r.groupby(["st_id", "pathway_name"]).size().reset_index(name="n_genes")
             .sort_values(["n_genes", "st_id"], ascending=[False, True]).head(30))
    top.to_csv(config.TABLES / "reactome_top_pathways.csv", index=False)

    rel = pd.read_csv(config.GRAPH_OUT / "relations.csv")
    low = rel[rel["grade"].isin(["D", "E"])].copy()
    low.to_csv(config.TABLES / "low_evidence_edges.csv", index=False)

    lines = ["# Enrichment and low-evidence summary", "",
             f"Total enriched GO terms: {len(pd.read_csv(config.DATA_PROCESSED / 'enrichr_GO_Biological_Process_2023.csv'))}", "",
             "## Top 15 GO Biological Process terms (Enrichr)", "",
             "| Term | Adjusted p | Genes |", "|---|---:|---|"]
    for _, x in e.head(15).iterrows():
        lines.append(f"| {x['term']} | {x['adjusted_p_value']:.2e} | {x['genes']} |")
    lines += ["", "## Top Reactome pathways by number of CHD-panel genes", "",
              "| Pathway | Genes |", "|---|---:|"]
    for _, x in top.head(10).iterrows():
        lines.append(f"| {x['pathway_name']} | {x['n_genes']} |")
    lines += ["", f"Low-evidence edges (grade D/E): **{len(low)}** of {len(rel)} relations. See `outputs/tables/low_evidence_edges.csv`."]
    (config.REPORTS / "enrichment_summary.md").write_text("\n".join(lines), encoding="utf-8")
    log.info("top30 GO terms, top30 pathways, %s low-evidence edges", len(low))


if __name__ == "__main__":
    main()
