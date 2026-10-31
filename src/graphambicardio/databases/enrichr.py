"""Enrichr (GO Biological Process) over-representation for the CHD gene set.

Used as a secondary, orthogonal annotation source to Reactome.  Enrichr output
is reported as *statistical over-representation in a gene list*, never as
evidence of a causal mechanism.
"""

from __future__ import annotations

import json
from typing import Any

from .. import config
from ..io_utils import get_logger, http_get, http_post, today, write_csv

log = get_logger("enrichr")

BASE = "https://maayanlab.cloud/Enrichr"


def add_list(genes: list[str], description: str = "GraphAmbiCardio CHD gene set") -> int:
    from ..io_utils import session

    r = session().post(
        f"{BASE}/addList",
        files={
            "list": (None, chr(10).join(genes)),
            "description": (None, description),
        },
        timeout=120,
    )
    r.raise_for_status()
    return int(r.json()["userListId"])


def enrich(user_list_id: int, library: str = "GO_Biological_Process_2023") -> list[dict[str, Any]]:
    data = json.loads(
        http_get(f"{BASE}/enrich", {"userListId": user_list_id, "backgroundType": library}, cache=False)
    )
    rows = []
    for term in data.get(library, []):
        # [rank, term, pvalue, zscore, combined_score, genes, adj_pvalue, ...]
        rows.append(
            {
                "library": library,
                "rank": term[0],
                "term": term[1],
                "p_value": term[2],
                "z_score": term[3],
                "combined_score": term[4],
                "genes": ";".join(term[5]) if isinstance(term[5], list) else term[5],
                "adjusted_p_value": term[6] if len(term) > 6 else "",
                "retrieved_at": today(),
                "source": "Enrichr",
            }
        )
    write_csv(config.DATA_PROCESSED / f"enrichr_{library}.csv", rows)
    log.info("Enrichr %s: %s terms", library, len(rows))
    return rows
