"""Recompute the PRISMA-style flow including SciELO (Crossref) and CAPES."""
from __future__ import annotations

import glob
import json
import os
import re
from collections import Counter

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())[:200]


def record_key(pmid="", doi="", title=""):
    if pmid:
        return "pmid:" + str(pmid)
    if doi:
        return "doi:" + str(doi).lower()
    return "title:" + norm_title(title)


rows = []
for path in glob.glob(os.path.join(ROOT, "literature", "searches", "*.json")):
    name = os.path.basename(path)
    data = json.load(open(path, encoding="utf-8"))
    if name.endswith("_europepmc.json"):
        source = "Europe PMC"
        items = data.get("studies", [])
    elif name.startswith("scielo_"):
        source = "SciELO (Crossref 10.1590)"
        items = data.get("items", [])
    elif name.startswith("capes_"):
        source = "CAPES Teses"
        items = data.get("items", [])
    elif name.startswith("pair_"):
        source = "PubMed (pares)"
        items = data.get("studies", [])
    else:
        source = "PubMed (domínios)"
        items = data.get("studies", [])
    for it in items:
        rows.append({
            "source": source,
            "key": record_key(str(it.get("pmid", "") or ""), it.get("doi", "") or "", it.get("title", "") or it.get("titulo", "") or ""),
            "title": it.get("title") or it.get("titulo") or "",
        })

df = pd.DataFrame(rows)
by_source = df.groupby("source").size().reset_index(name="records")
# remove exact duplicate rows from repeated pair searches within PubMed
df_unique_within = df.drop_duplicates(subset=["source", "key"])
raw_total = len(df)
total = len(df_unique_within)
dedup = df_unique_within.drop_duplicates(subset=["key"])
dups = raw_total - len(dedup)
flow = [
    {"stage": "PubMed (domínios + pares)", "records": int(by_source.loc[by_source.source.str.startswith("PubMed"), "records"].sum()), "notes": "top 100/domínio e top 15/par"},
    {"stage": "Europe PMC", "records": int(by_source.loc[by_source.source == "Europe PMC", "records"].sum()), "notes": "top 100/domínio"},
    {"stage": "SciELO (Crossref)", "records": int(by_source.loc[by_source.source.str.startswith("SciELO"), "records"].sum()), "notes": "5 consultas, 100 registros cada"},
    {"stage": "CAPES Teses", "records": int(by_source.loc[by_source.source == "CAPES Teses", "records"].sum()), "notes": "4 consultas"},
    {"stage": "Total bruto recuperado", "records": raw_total, "notes": "inclui repetições entre as buscas por pares"},
    {"stage": "Duplicatas removidas", "records": dups, "notes": "repetições entre buscas + PMID/DOI/título normalizado"},
    {"stage": "Registros únicos", "records": len(dedup), "notes": "triagem por título/resumo"},
]
pd.DataFrame(flow).to_csv(os.path.join(ROOT, "reports", "prisma_flow.csv"), index=False)
print(pd.DataFrame(flow).to_string(index=False))
print("\nby source:\n", by_source.to_string(index=False))
