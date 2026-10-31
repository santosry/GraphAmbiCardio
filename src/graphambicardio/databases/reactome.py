"""Reactome pathway over-representation per gene.

The Reactome Analysis Service (analysis, projection) is queried once per gene
so that gene->pathway edges keep an explicit, per-edge provenance.  Only
pathways with FDR < 0.05 are retained.
"""

from __future__ import annotations

import json
from typing import Any

from .. import config
from ..io_utils import get_logger, http_post, today, write_csv, write_json

log = get_logger("reactome")


def analyse(identifiers: list[str], page_size: int = 50) -> dict[str, Any]:
    raw = http_post(
        f"{config.REACTOME_ANALYSIS}/identifiers/projection",
        data="\n".join(identifiers),
        params={"pageSize": page_size, "page": 1},
        headers={"Content-Type": "text/plain", "Accept": "application/json"},
        timeout=120,
    )
    return json.loads(raw)


def collect_genes(genes: list[str], fdr_cutoff: float = 0.05, page_size: int = 30) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    summary = []
    for gene in genes:
        try:
            data = analyse([gene], page_size=page_size)
        except Exception as exc:  # noqa: BLE001
            log.warning("Reactome failed for %s: %s", gene, exc)
            summary.append({"gene_symbol": gene, "pathways_found": 0, "pathways_fdr005": 0, "error": str(exc)})
            continue
        pathways = data.get("pathways", [])
        sig = [p for p in pathways if p.get("entities", {}).get("fdr", 1) < fdr_cutoff]
        summary.append(
            {
                "gene_symbol": gene,
                "pathways_found": data.get("pathwaysFound", len(pathways)),
                "pathways_fdr005": len(sig),
                "error": "",
                "retrieved_at": today(),
            }
        )
        for p in sig:
            rows.append(
                {
                    "gene_symbol": gene,
                    "st_id": p.get("stId", ""),
                    "db_id": p.get("dbId", ""),
                    "pathway_name": p.get("name", ""),
                    "species": (p.get("species") or {}).get("name", ""),
                    "tax_id": (p.get("species") or {}).get("taxId", ""),
                    "entities_total": p.get("entities", {}).get("total", ""),
                    "entities_found": p.get("entities", {}).get("found", ""),
                    "p_value": p.get("entities", {}).get("pValue", ""),
                    "fdr": p.get("entities", {}).get("fdr", ""),
                    "in_disease": p.get("inDisease", ""),
                    "is_low_level_pathway": p.get("llp", ""),
                    "source": "Reactome Analysis Service (projection, over-representation)",
                    "retrieved_at": today(),
                }
            )
        log.info("Reactome %s: %s pathways, %s with FDR<%.2f", gene, len(pathways), len(sig), fdr_cutoff)
    write_csv(config.DATA_PROCESSED / "reactome_gene_pathway_edges.csv", rows)
    write_csv(config.DATA_PROCESSED / "reactome_gene_summary.csv", summary)
    write_json(config.DATA_PROCESSED / "reactome_raw_summary.json", summary)
    return rows
