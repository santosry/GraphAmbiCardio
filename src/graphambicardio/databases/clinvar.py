"""ClinVar retrieval through NCBI E-utilities.

ClinVar is used only as a *curated variant annotation* source.  A variant being
classified as pathogenic is not, by itself, evidence that the gene causes the
epidemiological phenotype under study: the trait recorded in ClinVar is kept
verbatim and reported with every edge.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any

from .. import config
from ..io_utils import get_json, get_logger, http_get, today, write_csv, write_json

log = get_logger("clinvar")

CHD_TRAIT_PATTERN = (
    "heart|cardiac|septal|ventric|atrial|tetralogy|fallot|coarctation|ductus|"
    "valve|truncus|arter|pulmonary|aort|ebstein|hypoplastic|heterotax|sit inversus"
)


def esearch_gene(gene: str, retmax: int = 200) -> dict[str, Any]:
    q = f'{gene}[gene] AND (pathogenic[clinsig] OR "likely pathogenic"[clinsig])'
    params = {
        "db": "clinvar",
        "term": q,
        "retmode": "json",
        "retmax": retmax,
        "tool": config.NCBI_TOOL,
        "email": config.NCBI_EMAIL,
    }
    if config.NCBI_API_KEY:
        params["api_key"] = config.NCBI_API_KEY
    time.sleep(0.11 if config.NCBI_API_KEY else 0.36)
    data = json.loads(http_get(f"{config.PUBMED_BASE}/esearch.fcgi", params))
    res = data["esearchresult"]
    return {"count": int(res.get("count", 0)), "ids": res.get("idlist", []), "query": q}


def esummary(ids: list[str]) -> list[dict[str, Any]]:
    out = []
    for i in range(0, len(ids), 100):
        chunk = ids[i : i + 100]
        params = {
            "db": "clinvar",
            "id": ",".join(chunk),
            "retmode": "json",
            "tool": config.NCBI_TOOL,
            "email": config.NCBI_EMAIL,
        }
        if config.NCBI_API_KEY:
            params["api_key"] = config.NCBI_API_KEY
        time.sleep(0.11 if config.NCBI_API_KEY else 0.36)
        data = json.loads(http_get(f"{config.PUBMED_BASE}/esummary.fcgi", params))
        result = data.get("result", {})
        for uid in result.get("uids", []):
            rec = result.get(uid, {})
            out.append(_flatten(rec))
    return out


def _flatten(rec: dict[str, Any]) -> dict[str, Any]:
    def desc(key: str) -> str:
        val = rec.get(key)
        if isinstance(val, dict):
            return str(val.get("description") or val.get("value") or "")
        return str(val or "")

    gc = rec.get("germline_classification") or {}
    genes = ";".join(g.get("symbol", "") for g in (rec.get("genes") or []) if isinstance(g, dict))
    traits = ";".join(
        t.get("trait_name", "") for t in (gc.get("trait_set") or []) if isinstance(t, dict)
    )
    var_set = rec.get("variation_set") or [{}]
    var = var_set[0] if isinstance(var_set, dict) else {}
    consequences = ";".join(rec.get("molecular_consequence_list") or [])
    return {
        "clinvar_uid": rec.get("uid", ""),
        "accession": rec.get("accession", ""),
        "accession_version": rec.get("accession_version", ""),
        "obj_type": rec.get("obj_type", ""),
        "title": rec.get("title", ""),
        "gene_symbol": genes,
        "germline_classification": str(gc.get("description", "")),
        "clinical_significance": desc("clinical_significance"),
        "trait_set": traits,
        "variation_name": var.get("variation_name", "") if isinstance(var, dict) else "",
        "cdna_change": var.get("cdna_change", "") if isinstance(var, dict) else "",
        "molecular_consequence": consequences,
        "review_status": str(gc.get("review_status", "")),
        "last_evaluated": str(gc.get("last_evaluated", "")),
    }


def collect_genes(genes: list[str], per_gene: int = 40) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    counts = []
    for gene in genes:
        search = esearch_gene(gene, retmax=per_gene)
        records = esummary(search["ids"][:per_gene]) if search["ids"] else []
        # Large CNVs list hundreds of overlapping genes in `genes`; they are not
        # gene-specific evidence and would create spurious gene nodes.
        records = [r for r in records if not str(r.get("title", "")).startswith("GRCh")]
        records = [
            r for r in records
            if re.search(r"pathogenic", r.get("germline_classification", ""), flags=re.I)
            and not re.search(r"conflicting|uncertain", r.get("germline_classification", ""), flags=re.I)
        ]
        chd = [r for r in records if re.search(CHD_TRAIT_PATTERN, r["trait_set"], flags=re.I)]
        counts.append(
            {
                "gene_symbol": gene,
                "n_pathogenic_or_likely_pathogenic": search["count"],
                "n_retrieved": len(records),
                "n_chd_related_trait": len(chd),
                "query": search["query"],
                "retrieved_at": today(),
            }
        )
        for r in records:
            r["query_gene"] = gene
            r["chd_related_trait"] = bool(re.search(CHD_TRAIT_PATTERN, r["trait_set"], flags=re.I))
            r["retrieved_at"] = today()
            rows.append(r)
        log.info("ClinVar %s: %s pathogenic/likely pathogenic, %s retrieved, %s CHD-trait", gene, search["count"], len(records), len(chd))
    write_csv(config.DATA_PROCESSED / "clinvar_gene_counts.csv", counts)
    write_csv(config.DATA_PROCESSED / "clinvar_variants.csv", rows)
    write_json(config.DATA_PROCESSED / "clinvar_variants.json", rows)
    return rows
