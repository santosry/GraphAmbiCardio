"""Build a separate graph of automatically screened studies.

This graph is intentionally **not** merged with the evidence graph. It shows
what the exhaustive retrieval found and how the automated triage tagged each
record. A Study node here is a candidate, not an evidence anchor.

Outputs:
  outputs/graph/screened_studies.graphml
  outputs/graph/screened_studies.json
  outputs/graph/screened_study_nodes.csv
  outputs/graph/screened_study_relations.csv
  reports/screened_studies.json
  reports/screened_studies.md
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import networkx as nx
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from graphambicardio.io_utils import today, write_csv, write_json  # noqa: E402

CANDIDATES = ROOT / "literature" / "screening" / "exhaustive_candidates.csv"
GRAPH_OUT = ROOT / "outputs" / "graph"
REPORTS = ROOT / "reports"


def study_id(key: str) -> str:
    return "STUDY:" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]


def clean(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def split(value: Any) -> list[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    return [x.strip() for x in str(value).split(";") if x.strip()]


def main() -> None:
    df = pd.read_csv(CANDIDATES, low_memory=False)
    known_nodes = pd.read_csv(GRAPH_OUT / "nodes.csv")
    known_targets = set(known_nodes["node_id"])
    G = nx.DiGraph()
    node_rows: list[dict[str, Any]] = []
    rel_rows: list[dict[str, Any]] = []

    for _, r in df.iterrows():
        sid = study_id(str(r["candidate_key"]))
        species = ";".join(
            x for x, flag in (("human", r.get("species_human")), ("animal", r.get("species_animal")), ("cell", r.get("species_cell"))) if bool(flag)
        )
        pmid = clean(r.get("pmid"))
        doi = clean(r.get("doi"))
        ref = pmid or doi or clean(r.get("candidate_key"))
        node = {
            "node_id": sid,
            "label": str(r.get("title", ""))[:180],
            "type": "Study",
            "subtype": "screened_candidate",
            "identifiers": ";".join(x for x in (f"PMID:{pmid}" if pmid else "", f"DOI:{doi}" if doi else "") if x),
            "description": f"{r.get('year', '')} | {r.get('journal', '')} | {r.get('design', '')} | {r.get('sources', '')}",
            "source": "exhaustive retrieval + automated triage",
        }
        G.add_node(sid, **node)
        node_rows.append(node)

        targets: list[tuple[str, str]] = []
        targets += [("Exposure", x) for x in split(r.get("exposures"))]
        targets += [("Phenotype", x) for x in split(r.get("phenotypes"))]
        targets += [("Mechanism", x) for x in split(r.get("mechanisms"))]
        seen = set()
        for target_type, target in targets:
            if target in seen or target not in known_targets:
                continue
            seen.add(target)
            rel = {
                "source_id": sid,
                "source_type": "Study",
                "target_id": target,
                "target_type": target_type,
                "relation": "STUDY_DOCUMENTS_RELATION",
                "layer": "screened",
                "confidence": 0.0,
                "grade": "E",
                "evidence_type": "screened_record",
                "study_design": str(r.get("design", "")),
                "species": species,
                "reference": ref,
                "reference_type": "PMID/DOI" if (pmid or doi) else "title",
                "source_database": str(r.get("sources", "")),
                "retrieved_at": today(),
                "notes": "Automated triage only. Not manually curated and not an evidence edge.",
            }
            G.add_edge(sid, target, key=f"{sid}|{target}", **rel)
            rel_rows.append(rel)

    write_csv(GRAPH_OUT / "screened_study_nodes.csv", node_rows)
    write_csv(GRAPH_OUT / "screened_study_relations.csv", rel_rows)
    nx.write_graphml(G, GRAPH_OUT / "screened_studies.graphml")
    write_json(GRAPH_OUT / "screened_studies.json", nx.node_link_data(G, edges="edges"))

    by_source: dict[str, int] = {}
    for _, r in df.iterrows():
        for s in split(r.get("sources")):
            by_source[s] = by_source.get(s, 0) + 1
    summary = {
        "generated_at": today(),
        "status": "screened candidates; NOT evidence",
        "n_studies": len(node_rows),
        "n_relations": len(rel_rows),
        "n_studies_with_chd_phenotype": int(df["phenotypes"].notna().sum()),
        "by_source": by_source,
        "note": "Study nodes are automatically screened retrieved records. They are kept separate from the manually curated evidence graph.",
    }
    write_json(REPORTS / "screened_studies.json", summary)
    lines = [
        "# Estudos triados: camada separada, não evidência",
        "",
        f"Gerado: {today()}",
        "",
        f"**Estudos candidatos:** {summary['n_studies']:,}  ",
        f"**Relações estudo→conceito:** {summary['n_relations']:,}  ",
        f"**Com fenótipo CHD detectado:** {summary['n_studies_with_chd_phenotype']:,}",
        "",
        "| Base | Estudos candidatos |",
        "|---|---:|",
    ]
    for source, n in sorted(by_source.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {source} | {n:,} |")
    lines += [
        "",
        "Esta camada é gerada por triagem automática e **não entra** em `evidence.csv`, nos caminhos, na centralidade ou nas conclusões. "
        "Ela serve para auditoria e priorização de curadoria. Um estudo só se torna evidência após leitura manual, extração de trecho verbatim e gradação.",
        "",
        "Arquivos: `outputs/graph/screened_studies.json`, `outputs/graph/screened_studies.graphml`, `outputs/graph/screened_study_nodes.csv`, `outputs/graph/screened_study_relations.csv`.",
    ]
    (REPORTS / "screened_studies.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"screened graph: {len(node_rows)} studies, {len(rel_rows)} relations")


if __name__ == "__main__":
    main()
