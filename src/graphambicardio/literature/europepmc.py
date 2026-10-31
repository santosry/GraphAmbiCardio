"""Europe PMC retrieval (REST API, no key required for the public endpoint).

Used as an independent discovery source and for open-access coverage; it is
never used as a substitute for PubMed when a PMID is available.
"""

from __future__ import annotations

import json
from typing import Any

from .. import config
from ..io_utils import get_logger, get_json, today, write_json

log = get_logger("europepmc")

BASE = config.EUROPEPMC_BASE


import re


def to_europepmc_query(query: str) -> str:
    """Translate the PubMed field-tagged query to Europe PMC syntax.

    Europe PMC does not understand ``[tiab]``/``[MeSH]``; the translation keeps
    the concept blocks (and therefore the recall/precision trade-off is
    documented) and is stored alongside every result.
    """
    q = re.sub(r'"([^"]+)"\[tiab\]', lambda m: f'TITLE_ABS:"{m.group(1)}"', query)
    q = re.sub(r'"([^"]+)"\[MeSH\]', lambda m: f'MESH:"{m.group(1)}"', q)
    q = re.sub(r'"(\w+)\*"\[tiab\]', lambda m: f'TITLE_ABS:{m.group(1)}*', q)
    q = re.sub(r'"(\w+)\*"\[MeSH\]', lambda m: f'MESH:{m.group(1)}*', q)
    return q


def search(query: str, page_size: int = 100, result_type: str = "core") -> dict[str, Any]:
    params = {
        "query": query,
        "format": "json",
        "pageSize": min(page_size, 1000),
        "resultType": result_type,
    }
    data = get_json(f"{BASE}/search", params)
    return {
        "database": "Europe PMC",
        "query": query,
        "query_translation": to_europepmc_query(query),
        "retrieved_at": today(),
        "count_total": data.get("hitCount", 0),
        "results": data.get("resultList", {}).get("result", []),
    }


def run_search(name: str, query: str, page_size: int = 100) -> dict[str, Any]:
    rec = search(to_europepmc_query(query), page_size=page_size)
    rec["query_pubmed_original"] = query
    flat = []
    for r in rec["results"]:
        flat.append(
            {
                "pmid": r.get("pmid", ""),
                "doi": r.get("doi", ""),
                "title": r.get("title", ""),
                "journal": r.get("journalTitle", ""),
                "year": str(r.get("pubYear", "")),
                "first_author": r.get("authorString", "").split(",")[0],
                "abstract": r.get("abstractText", ""),
                "pubtypes": ";".join(
                    p.get("name", "") if isinstance(p, dict) else str(p)
                    for p in (r.get("pubTypeList", {}) or {}).get("pubType", [])
                ),
                "is_open_access": r.get("isOpenAccess", ""),
                "source": r.get("source", ""),
            }
        )
    rec["studies"] = flat
    rec.pop("results", None)
    write_json(config.SEARCHES / f"{name}_europepmc.json", rec)
    log.info("%s (Europe PMC): %s hits, %s retrieved", name, rec["count_total"], len(flat))
    return rec
