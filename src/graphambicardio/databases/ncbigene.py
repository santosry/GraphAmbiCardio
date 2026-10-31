"""NCBI Gene metadata for the gene panel (stable NCBI Gene IDs)."""

from __future__ import annotations

import json
import time
from typing import Any

from .. import config
from ..io_utils import get_logger, http_get, today, write_csv, write_json

log = get_logger("ncbigene")


def esearch_symbol(symbol: str) -> str:
    params = {
        "db": "gene",
        "term": f"{symbol}[gene] AND Homo sapiens[orgn]",
        "retmode": "json",
        "retmax": 1,
        "tool": config.NCBI_TOOL,
        "email": config.NCBI_EMAIL,
    }
    if config.NCBI_API_KEY:
        params["api_key"] = config.NCBI_API_KEY
    time.sleep(0.11 if config.NCBI_API_KEY else 0.36)
    data = json.loads(http_get(f"{config.PUBMED_BASE}/esearch.fcgi", params))
    ids = data["esearchresult"].get("idlist", [])
    return ids[0] if ids else ""


def esummary_gene(gene_id: str) -> dict[str, Any]:
    params = {
        "db": "gene",
        "id": gene_id,
        "retmode": "json",
        "tool": config.NCBI_TOOL,
        "email": config.NCBI_EMAIL,
    }
    if config.NCBI_API_KEY:
        params["api_key"] = config.NCBI_API_KEY
    time.sleep(0.11 if config.NCBI_API_KEY else 0.36)
    data = json.loads(http_get(f"{config.PUBMED_BASE}/esummary.fcgi", params))
    rec = data["result"].get(gene_id, {})
    return {
        "ncbi_gene_id": gene_id,
        "symbol": rec.get("name", ""),
        "description": rec.get("description", ""),
        "other_designations": ";".join(rec.get("otherdesignations", [])[:5]),
        "chromosome": rec.get("chromosome", ""),
        "map_location": rec.get("maplocation", ""),
        "gene_type": rec.get("genetypes", [""])[0] if rec.get("genetypes") else "",
        "ensembl_ids": ";".join(
            x.get("value", "") for x in rec.get("genomicinfo", []) if isinstance(x, dict)
        ),
        "retrieved_at": today(),
    }


def collect(genes: list[str]) -> list[dict[str, Any]]:
    rows = []
    for g in genes:
        try:
            gid = esearch_symbol(g)
            if not gid:
                rows.append({"symbol": g, "ncbi_gene_id": "", "retrieved_at": today(), "error": "not found"})
                continue
            rec = esummary_gene(gid)
            rec["symbol"] = rec.get("symbol") or g
            rows.append(rec)
            log.info("Gene %s -> %s", g, gid)
        except Exception as exc:  # noqa: BLE001
            rows.append({"symbol": g, "ncbi_gene_id": "", "retrieved_at": today(), "error": str(exc)})
    write_csv(config.DATA_PROCESSED / "ncbi_gene_metadata.csv", rows)
    write_json(config.DATA_PROCESSED / "ncbi_gene_metadata.json", rows)
    return rows
